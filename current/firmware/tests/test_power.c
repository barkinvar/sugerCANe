#include "power.h"
#include <assert.h>
#include <stdio.h>
static void run(sc_power *p,uint32_t a,uint32_t b,uint16_t v12,uint16_t v5,uint8_t fault) {
 for(uint32_t t=a;t<=b;t++)sc_power_update(p,t,true,v12,v5,fault);
}
int main(void) {
 sc_power p;sc_power_init(&p,0,true);assert(!p.enabled&&p.pending==3);
 run(&p,1,9,0,0,0);assert(p.enabled==0);
 run(&p,10,59,0,5000,0);assert(p.enabled==2);
 run(&p,60,160,12000,5000,0);assert(p.enabled==3&&p.good==3);
 run(&p,161,170,10700,5000,0);assert(p.enabled==3&&p.good==2);
 run(&p,171,275,12000,5000,0);assert(p.enabled==3&&p.good==3);
 run(&p,276,300,0,5000,0);assert(p.enabled==2&&p.latched==1);
 run(&p,301,1000,12000,5000,0);assert(p.enabled==2&&p.latched==1); /* no auto-retry */
 sc_power_restart(&p,1,1000);assert(p.enabled==2&&p.pending==1&&!p.latched);
 run(&p,1001,1059,0,5000,0);assert(p.enabled==2);
 run(&p,1060,1200,12000,5000,0);assert(p.enabled==3&&p.good==3);
 sc_power_update(&p,1201,true,12000,5000,2);assert(p.enabled==1&&p.latched==2);
 sc_power_update(&p,1202,true,13100,0,0);assert(p.enabled==0&&p.latched==3);
 sc_power_init(&p,0,true);run(&p,1,300,0,0,0);assert(p.latched==3&&p.enabled==0);
 sc_power_init(&p,0,true);sc_power_update(&p,1,false,0,0,0);assert(p.latched==3&&!p.pending);
 sc_power_init(&p,0,false);sc_power_restart(&p,3,500);assert(!p.enabled&&!p.pending&&p.latched==3);
 sc_power_init(&p,0xfffffff0u,true);
 for(uint32_t dt=1;dt<200;dt++)sc_power_update(&p,0xfffffff0u+dt,true,12000,5000,0);
 assert(p.enabled==3&&p.good==3);
 sc_power_init(&p,0,true);run(&p,1,300,11160,4600,0);
 assert(p.enabled==3&&p.good==3&&!p.latched); /* valid low corner with ADC error */
 run(&p,301,450,12790,5450,0);assert(p.enabled==3&&p.good==3);
 run(&p,451,480,10750,4350,0);assert(!p.enabled&&p.latched==3);
 puts("power: staggered enables, startup timeout, low-voltage deglitch, independent fault latches, deliberate restart, ADC failure and timer wrap passed");
}
