#include "board.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
int firmware_main(void);
host_gpio host_gpioa;host_rcc host_rcc_state={.CSR=RCC_CSR_PORRSTF};host_can host_can_state;
volatile uint32_t board_millis;uint32_t SystemCoreClock=48000000;
static jmp_buf done;static const char *scenario;static unsigned feeds,aborts,sends,stores,stops;static bool standby=true;
static char serial[8192];static const char *input="";static unsigned serial_pos;
static sc_config_record config={.device_id=17,.debounce_ms=2},saved;
typedef struct {uint32_t at,id;uint8_t len,d[8];} frame;
static frame tx[512],rx[32];static unsigned nrx,irx;
static bool is(const char *s){return !strcmp(scenario,s);}
static void cmd(unsigned at,unsigned api,unsigned invert,unsigned db,unsigned version,unsigned reserved) {
 frame *f=&rx[nrx++];*f=(frame){.at=at,.id=sc_can_id(17,api),.len=8,.d={0x53,0x43,version,invert,db,0,reserved,0}};
}
void board_gpio_init(void){} void board_voltage_guard_init(void){} bool board_clock_init(void){return !is("clock_failure");}
int SysTick_Config(uint32_t ticks){assert(ticks==48000);return 0;}
void board_uart_init(void){} void board_uart_flush(void){} void board_watchdog_start(void){} void board_watchdog_feed(void){feeds++;}
void board_uart_write(const char *s){assert(strlen(serial)+strlen(s)<sizeof(serial));strcat(serial,s);}
int board_uart_get(void){return board_millis>=50 && input[serial_pos] ? (unsigned char)input[serial_pos++] : -1;}
const sc_config_record *board_config_load(void){return is("unconfigured")?0:&config;}
bool board_config_store(sc_config_record *r){saved=*r;stores++;return true;}
_Noreturn void NVIC_SystemReset(void){longjmp(done,2);}
void board_can_standby(bool x){standby=x;} void board_can_abort(void){aborts++;}
bool board_can_init(uint8_t id){assert(id==17);return !is("can_failure");}
bool board_can_send(uint32_t id,const uint8_t d[8]) {
 assert(!standby && sends<512);tx[sends]=(frame){.at=board_millis,.id=id,.len=8};memcpy(tx[sends++].d,d,8);return !is("busy");
}
bool board_can_receive(uint32_t *id,uint8_t d[8],uint8_t *len){if(irx==nrx||rx[irx].at>board_millis)return false;frame *f=&rx[irx++];*id=f->id;*len=f->len;memcpy(d,f->d,8);return true;}
void board_status_led(bool on){(void)on;}
void board_safe_off(void){standby=true;stops++;longjmp(done,3);}
void host_wait(void){if(board_millis>=1200)longjmp(done,1);board_millis+=(is("stall") && board_millis==49)?21:1;host_gpioa.IDR=((board_millis>=150 && board_millis<170)?7u:0u)|24u;
 if((is("rail12_fault")||is("rail5_fault")) && board_millis>=300 && board_millis<350)host_gpioa.IDR &= ~(is("rail12_fault")?8u:16u);
 if(is("rail_chatter") && board_millis>=300 && board_millis<500 && board_millis%20<10)host_gpioa.IDR &= ~8u;
 if((is("rail12_fault")||is("rail5_fault")||is("rail_chatter")) && board_millis>=310 && board_millis<330)host_gpioa.IDR |= 7u;}
int main(int argc,char **argv) {
 assert(argc==2);scenario=argv[1];
 if(is("disable")){rx[nrx++]=(frame){.at=20,.id=0,.len=0};cmd(100,SC_API_RESUME,0,0,3,0);}
 if(is("config")){cmd(40,SC_API_CONFIG,4,4,3,0);}
 if(is("bad_commands")){cmd(40,SC_API_CONFIG,4,4,1,0);cmd(50,SC_API_CONFIG,4,4,3,1);cmd(60,SC_API_CONFIG,8,4,3,0);cmd(70,0x200,4,4,3,0);}
 if(is("uart"))input="SET 3 5 7\n";
 if(is("old_uart"))input="SET 3 5 7 3\n";
 if(is("overflow"))input="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\nSET 18 2 4\n";
 int result=setjmp(done);if(!result)firmware_main();
 if(is("uart")||is("overflow")){assert(result==2&&stores==1);assert(saved.device_id==(is("uart")?3:18));assert(saved.reserved_power==0);}
 else if(is("stall")){assert(result==3&&stops==1&&standby&&feeds==49);}
 else {
  assert(feeds==1200);
  if(is("unconfigured")||is("clock_failure")||is("can_failure")){assert(sends==0&&standby);}
  else {
   assert(sends>100);unsigned statuses=0,identities=0,counts=0,diagnostics=0;
   for(unsigned i=0;i<sends;i++) {
    frame *f=&tx[i];unsigned api=(f->id>>6)&1023;
    if(is("disable"))assert(f->at<20||f->at>=100);
    if(api==SC_API_STATUS){statuses++;assert(f->d[0]==3&&f->d[4]==3&&f->d[5]==0x3f);assert(f->d[2]<8&&f->d[3]<8);if(f->at>=600)assert(f->d[2]==(is("config")?4:0));
     unsigned rail=(f->d[6]>>4)&3; if(f->at<100)assert(rail==0);if(f->at>=600)assert(rail==3);
     if(f->at>=300&&f->at<=440){if(is("rail12_fault"))assert(!(rail&1));if(is("rail5_fault"))assert(!(rail&2));}
     if(is("rail_chatter") && f->at>=300&&f->at<=580)assert(!(rail&1));}
    if(api==SC_API_IDENTITY){identities++;assert(f->d[0]==3&&f->d[1]==0&&f->d[2]==4&&f->d[4]==4&&f->d[5]==17);assert(f->d[7]==(is("config")?4:0));}
    if(api==SC_API_COUNTS34){counts++;assert(f->d[0]==(f->at>=200?1:0)&&f->d[4]==0&&f->d[5]==0&&f->d[6]==0&&f->d[7]==0);}
    if(api==SC_API_DIAGNOSTIC){diagnostics++;if(is("busy"))assert(f->d[0]>0);}
   }
   assert(statuses>100&&identities==1&&counts>5&&diagnostics>5);
   assert(aborts==(is("disable")?1u:0u));
  }
  assert(stores==0);
 }
 printf("application: %s passed (%u frames, %u scheduler feeds)\n",scenario,sends,feeds);
}
