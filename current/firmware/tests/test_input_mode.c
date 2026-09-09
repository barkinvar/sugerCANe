#include "input_mode.h"
#include <assert.h>
#include <stdio.h>
static void tick(sc_input_modes*s,unsigned time,unsigned driven_high,unsigned driven_low){
 unsigned pins=(driven_high|s->up)&~driven_low;sc_input_modes_update(s,pins,time);assert(!(s->up&s->down));
}
int main(void){
 sc_input_modes s;unsigned valid=0;
 for(unsigned w=0;w<(1u<<18);w++)valid+=sc_input_config_valid(w);
 assert(valid==27000);assert(!sc_input_config_valid(1u<<18));
 /* Mixed fixed biases and independent active polarities. */
 sc_input_modes_init(&s,1|(2<<3)|(1<<9),0);assert(s.up==1&&s.down==2&&!s.valid);
 tick(&s,1,4,1);assert(!s.valid);tick(&s,2,4,1);assert(s.valid==7&&s.logical==5);
 /* All three float channels: driven high, driven low, disconnected. */
 unsigned word=3|(3<<3)|(3<<6)|(2<<9)|(2<<12)|(3<<15);
 sc_input_modes_init(&s,word,0);
 for(unsigned t=1;t<=8;t++)tick(&s,t,1,2);
 assert(s.valid==7&&s.high==1&&s.floating==4&&s.logical==7);
 for(unsigned t=9;t<101;t++) {tick(&s,t,1,2);assert(s.valid==7&&s.logical==7);}
 /* Disconnect first input; invalidate then require repeat confirmation. */
 for(unsigned t=101;t<=108;t++)tick(&s,t,0,2);
 assert(s.valid==7&&s.floating==5&&s.logical==6);
 /* Impossible sample pair: low under pull-up, high under pull-down. */
 sc_input_modes_init(&s,3,0);tick(&s,2,0,1);tick(&s,4,1,0);assert(!(s.valid&1));
 /* Keeper starts low and follows a driven level, retaining it when released. */
 sc_input_modes_init(&s,4,0);tick(&s,2,1,0);assert(s.up==1);
 tick(&s,3,0,0);assert(s.high==1);tick(&s,4,0,1);assert(s.down==1);
 tick(&s,5,0,0);assert(s.high==0);
 /* Unsigned millisecond wrap must still permit settling. */
 sc_input_modes_init(&s,1,0xffffffffu);tick(&s,1,0,0);assert(s.valid==7);
 puts("input modes: exhaustive configuration validation, mixed polarity, float classification/confirmation, keeper, wrap passed");
}
