#include "board.h"
#include "board_service.h"
#include "power.h"
#include <string.h>
/* First 192 bytes are vectors; this validated, retained cookie is outside .bss. */
typedef struct {uint32_t magic,stay,crashes,crc;} boot_cookie;
#define COOKIE ((volatile boot_cookie *)0x200000c0u)
#define COOKIE_MAGIC 0x42524353u
static boot_cookie cookie_get(void) {
    boot_cookie c=*COOKIE;
    if(c.magic!=COOKIE_MAGIC || c.crc!=sc_crc32(&c,12))c=(boot_cookie){COOKIE_MAGIC,0,0,0};
    return c;
}
static void cookie_put(boot_cookie c){c.crc=sc_crc32(&c,12);*COOKIE=c;__DSB();}
void board_boot_request(bool stay) {boot_cookie c=cookie_get();c.stay=stay?1u:0u;c.crashes=0;cookie_put(c);NVIC_SystemReset();}
bool board_boot_stay(void) {
    boot_cookie c=cookie_get();
    if(RCC->CSR&RCC_CSR_PORRSTF)c=(boot_cookie){COOKIE_MAGIC,0,0,0};
    if(RCC->CSR&RCC_CSR_IWDGRSTF)c.crashes++;
    bool stay=c.stay==1 || c.crashes>=3;c.stay=0;cookie_put(c);
    return stay;
}
void board_boot_healthy(void){boot_cookie c=cookie_get();if(c.crashes){c.crashes=0;cookie_put(c);}}
static bool read_flash(void *ctx,uint32_t address,void *dst,uint32_t n) {
    (void)ctx;
    if(address<SC_APP_BASE || n>0x8000 || address>0x08008000u-n)return false;
    memcpy(dst,(const void *)address,n);return true;
}
static bool ready(void) {
    for(unsigned n=0;n<4000000;n++)if(!(FLASH->SR&FLASH_SR_BSY))return !(FLASH->SR&(FLASH_SR_PGERR|FLASH_SR_WRPRTERR));
    return false;
}
static void unlock(void){FLASH->KEYR=0x45670123u;FLASH->KEYR=0xcdef89abu;FLASH->SR=FLASH_SR_EOP|FLASH_SR_PGERR|FLASH_SR_WRPRTERR;}
static bool erase_flash(void *ctx,uint32_t address) {
    (void)ctx;
    if(address<SC_APP_BASE || address>SC_MANIFEST || address%1024)return false;
    uint32_t pm=__get_PRIMASK();__disable_irq();unlock();bool ok=ready();
    if(ok){FLASH->CR=FLASH_CR_PER;FLASH->AR=address;FLASH->CR|=FLASH_CR_STRT;ok=ready();}
    FLASH->CR=FLASH_CR_LOCK;__set_PRIMASK(pm);return ok;
}
static bool write_flash(void *ctx,uint32_t address,const void *data,uint32_t n) {
    (void)ctx;
    if(address<SC_APP_BASE || n>SC_APP_SIZE+1024u || address>SC_MANIFEST+1024u-n || (address&1u) || (n&1u))return false;
    uint32_t pm=__get_PRIMASK();__disable_irq();unlock();bool ok=ready();
    for(uint32_t k=0;ok && k<n;k+=2){uint16_t v;memcpy(&v,(const uint8_t *)data+k,2);FLASH->CR=FLASH_CR_PG;*(volatile uint16_t *)(address+k)=v;ok=ready();FLASH->CR=0;}
    FLASH->CR=FLASH_CR_LOCK;__set_PRIMASK(pm);return ok;
}
static bool send(void *ctx,const uint8_t *d){(void)ctx;return board_can_send(SC_SERVICE_TX,d);}
static bool load(void *ctx,sc_config_record *c){(void)ctx;const sc_config_record *p=board_config_load();if(!p)return false;*c=*p;return true;}
static bool save(void *ctx,sc_config_record *c){(void)ctx;bool ok=board_config_store(c);board_can_standby(false);return ok;}
static bool protected_boot(void *ctx){(void)ctx;return (FLASH->WRPR&255u)==252u;}
static void reset(void *ctx,bool stay){(void)ctx;board_boot_request(stay);}
#ifdef SC_APPLICATION
static bool power(void *ctx,uint8_t mask,uint32_t now) {
    (void)ctx;if(!sensor_power.available)return false;
    sc_power_restart(&sensor_power,mask,now);board_power_set(sensor_power.enabled);return true;
}
static uint32_t rails(void *ctx,unsigned index) {
    (void)ctx;
    return index ? sensor_power.enabled|((uint32_t)sensor_power.good<<8)|((uint32_t)sensor_power.latched<<16)|((uint32_t)sensor_power.pending<<24) : sensor_power.mv[0]|((uint32_t)sensor_power.mv[1]<<16);
}
#endif
void board_service_init(sc_service *s,bool boot) {
    const sc_service_io io={0,read_flash,erase_flash,write_flash,send,load,save,protected_boot,reset,
#ifdef SC_APPLICATION
        power,rails
#else
        0,0
#endif
    };
    sc_service_init(s,&io,(const uint8_t *)UID_BASE,boot);
}
__attribute__((naked,noreturn)) static void jump(uint32_t sp __attribute__((unused)),uint32_t pc __attribute__((unused))) {
    __asm volatile("msr msp, r0\n bx r1");
}
void board_run_application(void) {
    board_status_stop();
    board_can_standby(true);__disable_irq();SysTick->CTRL=0;SysTick->LOAD=0;SysTick->VAL=0;
    SCB->ICSR=SCB_ICSR_PENDSTCLR_Msk|SCB_ICSR_PENDSVCLR_Msk;
    NVIC->ICER[0]=0xffffffffu;NVIC->ICPR[0]=0xffffffffu;
    RCC->APB1RSTR|=RCC_APB1RSTR_CANRST;RCC->APB1RSTR&=~RCC_APB1RSTR_CANRST;
    RCC->CR|=RCC_CR_HSION;while(!(RCC->CR&RCC_CR_HSIRDY)){}
    RCC->CFGR=0;while(RCC->CFGR&RCC_CFGR_SWS){}
    RCC->CR&=~(RCC_CR_PLLON|RCC_CR_HSEON|RCC_CR_CSSON);
    RCC->CIR=0;__DSB();__ISB();
    const uint32_t *v=(const uint32_t *)SC_APP_BASE;jump(v[0],v[1]);
}
