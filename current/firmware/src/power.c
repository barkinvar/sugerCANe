#include "power.h"
#include <string.h>
sc_power sensor_power;
void sc_power_restart(sc_power *p,uint8_t mask,uint32_t now) {
    mask &= 3;
    p->enabled &= (uint8_t)~mask;
    p->good &= (uint8_t)~mask;
    if(!p->available)return;
    p->latched &= (uint8_t)~mask;
    p->pending |= mask;
    for(unsigned i=0;i<2;i++)if(mask & (1u<<i))p->requested[i]=now;
}
void sc_power_init(sc_power *p,uint32_t now,bool available) {
    memset(p,0,sizeof(*p));p->available=available;
    if(available)sc_power_restart(p,3,now);else p->latched=3;
}
static void trip(sc_power *p,uint8_t bit) {
    p->enabled &= (uint8_t)~bit;p->pending &= (uint8_t)~bit;
    p->good &= (uint8_t)~bit;p->latched |= bit;
}
void sc_power_update(sc_power *p,uint32_t now,bool valid,uint16_t mv12,uint16_t mv5,uint8_t fault) {
    p->mv[0]=mv12;p->mv[1]=mv5;
    if(!valid){trip(p,3);return;}
    for(unsigned i=0;i<2;i++) {
        uint8_t bit=(uint8_t)(1u<<i);
        /* Always hold EN inactive at least 10 ms; stagger 12 V by 50 ms. */
        if((p->pending&bit) && (uint32_t)(now-p->requested[i]) >= (i?10u:60u)) {
            p->pending &= (uint8_t)~bit;p->enabled |= bit;
            p->started[i]=now;p->healthy_since[i]=now;p->bad_since[i]=now;
        }
        if(!(p->enabled&bit))continue;
        uint16_t v=p->mv[i];
        if((fault&bit) || v>(i?5600u:13000u)){trip(p,bit);continue;}
        /* Include divider, VREFINT drift, ADC and leakage error in health bands.
           These indications are not precision voltage-compliance measurements. */
        bool healthy=v>=(i?4550u:11100u) && v<=(i?5500u:12900u);
        if(!healthy){p->good &= (uint8_t)~bit;p->healthy_since[i]=now;}
        else if((uint32_t)(now-p->healthy_since[i])>=100u)p->good |= bit;
        bool low=v<(i?4400u:10800u);
        if(!low)p->bad_since[i]=now;
        /* Startup has a bounded 200 ms grace period; no automatic fault retry. */
        if(low && (uint32_t)(now-p->started[i])>=200u && (uint32_t)(now-p->bad_since[i])>=20u)trip(p,bit);
    }
}
