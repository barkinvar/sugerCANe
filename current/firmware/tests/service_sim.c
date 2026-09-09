/* Real protocol engine with simulated flash/peripherals, not an MCU emulator. */
#include "service.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {
 sc_service s;uint8_t flash[32768],uid[12],reply[8];sc_config_record config;
 bool configured,protected_boot,has_reply,boot;unsigned writes,cut,steps;uint32_t now;
 jmp_buf power;
} sim;
static bool read_flash(void *v,uint32_t a,void *d,uint32_t n){sim *x=v;if(a<0x08000000||a+n>0x08008000)return false;memcpy(d,x->flash+a-0x08000000,n);return true;}
static void boundary(sim *x){if(++x->steps==x->cut)longjmp(x->power,1);}
static bool erase(void *v,uint32_t a){sim*x=v;assert(a>=SC_APP_BASE&&a<=SC_MANIFEST&&a%1024==0);x->writes++;for(unsigned i=0;i<1024;i+=2){boundary(x);memset(x->flash+a-0x08000000+i,255,2);}return true;}
static bool write_flash(void*v,uint32_t a,const void*d,uint32_t n){sim*x=v;assert(a>=SC_APP_BASE&&a+n<=SC_MANIFEST+1024&&!(n%2));x->writes++;for(unsigned i=0;i<n;i+=2){boundary(x);for(unsigned j=0;j<2;j++)x->flash[a-0x08000000+i+j]&=((const uint8_t*)d)[i+j];}return true;}
static bool send(void*v,const uint8_t*d){sim*x=v;memcpy(x->reply,d,8);x->has_reply=true;return true;}
static bool load(void*v,sc_config_record*c){sim*x=v;*c=x->config;return x->configured;}
static bool save(void*v,sc_config_record*c){sim*x=v;x->config=*c;x->configured=true;return true;}
static bool protected_boot(void*v){return ((sim*)v)->protected_boot;}
static bool power(void *ctx,uint8_t mask,uint32_t now){(void)ctx;(void)now;return mask>0&&mask<=3;}
static uint32_t rails(void *ctx,unsigned n){(void)ctx;return n?0x303u:(12000u|(5000u<<16));}
static void init(sim*x,bool boot);
static void reset(void*v,bool boot){sim*x=v;init(x,boot||!sc_image_valid(&x->s.io));}
static void init(sim*x,bool boot){sc_service_io io={x,read_flash,erase,write_flash,send,load,save,protected_boot,reset,power,rails};x->boot=boot;sc_service_init(&x->s,&io,x->uid,boot);}
void *sim_new(const uint8_t*uid,int boot){sim*x=calloc(1,sizeof(*x));assert(x);memset(x->flash,255,sizeof(x->flash));memcpy(x->uid,uid,12);x->protected_boot=true;init(x,boot!=0);return x;}
void sim_free(void*v){free(v);}
int sim_exchange(void*v,const uint8_t*d,uint8_t*out){sim*x=v;x->has_reply=false;sc_service_receive(&x->s,d,++x->now);sc_service_tick(&x->s,x->now);if(x->has_reply)memcpy(out,x->reply,8);return x->has_reply;}
void sim_tick(void*v,unsigned ms){sim*x=v;x->now+=ms;sc_service_tick(&x->s,x->now);}
void sim_protect(void*v,int on){((sim*)v)->protected_boot=on!=0;}
unsigned sim_writes(void*v){return ((sim*)v)->writes;}
int sim_valid(void*v){return sc_image_valid(&((sim*)v)->s.io);}
void sim_seed(void*v,const uint8_t*d,unsigned n){sim*x=v;assert(n<=SC_APP_SIZE);memcpy(x->flash+0x2000,d,n);uint32_t m[6]={SC_IMAGE_MAGIC,n,sc_crc32(d,n),SC_IMAGE_TAG,0,SC_IMAGE_COMMIT};m[4]=sc_crc32(m,16);memcpy(x->flash+0x7400,m,24);}
#ifndef SC_SIM_LIBRARY
static uint8_t seq;
static uint32_t command(sim*x,unsigned op,uint32_t value){uint8_t d[8]={(uint8_t)op,++seq,1,0},r[8];sc_put_u32(d+4,value);int reply=sim_exchange(x,d,r);if(op>=SC_PREFIX0&&op<=SC_PREFIX2)return 0;assert(reply&&r[0]==(op|0x80));return sc_get32(r+4);}
static void select_node(sim*x){command(x,SC_OPEN,SC_SERVICE_MAGIC);for(unsigned i=0;i<3;i++)command(x,SC_PREFIX0+i,sc_get32(x->uid+4*i));command(x,SC_PROBE,96);}
static void upload(sim*x,const uint8_t*d,unsigned n){select_node(x);command(x,SC_SIZE,n);command(x,SC_CRC,sc_crc32(d,n));command(x,SC_BEGIN,SC_IMAGE_TAG);for(unsigned i=0;i<n;i+=4){command(x,SC_OFFSET,i);assert(command(x,SC_DATA,sc_get32(d+i))==i+4);}command(x,SC_FINISH,0);}
int main(void){uint8_t uid[12]={1},old[1200],next[1200];memset(old,0x55,sizeof(old));memset(next,0xaa,sizeof(next));sc_put_u32(old,0x20001800);sc_put_u32(old+4,SC_APP_BASE+193);memcpy(next,old,8);
 sim*x=sim_new(uid,1);sim_seed(x,old,sizeof(old));upload(x,next,sizeof(next));unsigned boundaries=x->steps;assert(sim_valid(x));sim_free(x);
 for(unsigned cut=1;cut<=boundaries+1;cut++){
  x=sim_new(uid,1);sim_seed(x,old,sizeof(old));memset(x->flash,0x69,0x2000);memset(x->flash+0x7800,0x96,2048);x->cut=cut;
  if(!setjmp(x->power))upload(x,next,sizeof(next));
  x->cut=0;init(x,true);
  if(sim_valid(x))assert(!memcmp(x->flash+0x2000,old,sizeof(old))||!memcmp(x->flash+0x2000,next,sizeof(next)));
  for(unsigned i=0;i<0x2000;i++)assert(x->flash[i]==0x69);
  for(unsigned i=0x7800;i<0x8000;i++)assert(x->flash[i]==0x96);
  upload(x,next,sizeof(next));assert(sim_valid(x));assert(!memcmp(x->flash+0x2000,next,sizeof(next)));sim_free(x);
 }
 printf("service: %u simulated halfword erase/program power-cut boundaries + completed upload; every retry recovered, boot/config untouched\n",boundaries);
 return 0;
}
#endif
