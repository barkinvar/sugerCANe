#include "input_mode.h"
#include <string.h>
bool sc_input_config_valid(uint32_t config) {
    if(config>>18)return false;
    for(unsigned i=0;i<3;i++) {
        if(((config>>(3*i))&7u)>SC_BIAS_KEEPER ||
           ((config>>(9+3*i))&7u)>SC_ACTIVE_NOT_LOW)return false;
    }
    return true;
}
static void drive(sc_input_modes *s) {
    s->up=s->down=0;
    for(unsigned i=0;i<3;i++) {
        uint8_t bit=(uint8_t)(1u<<i),mode=(s->config>>(3*i))&7u;
        if(mode==SC_BIAS_UP || (mode==SC_BIAS_FLOAT && s->phase==0) ||
           (mode==SC_BIAS_KEEPER && (s->keeper&bit)))s->up|=bit;
        if(mode==SC_BIAS_DOWN || (mode==SC_BIAS_FLOAT && s->phase==1) ||
           (mode==SC_BIAS_KEEPER && !(s->keeper&bit)))s->down|=bit;
    }
}
void sc_input_modes_init(sc_input_modes *s,uint32_t config,uint32_t now) {
    memset(s,0,sizeof(*s));s->config=sc_input_config_valid(config)?config:0;
    s->switched_at=now;
    for(unsigned i=0;i<3;i++)s->state[i]=s->candidate[i]=SC_STATE_UNKNOWN;
    drive(s);
}
void sc_input_modes_update(sc_input_modes *s,uint8_t pins,uint32_t now) {
    pins&=7;
    /* Never feed probing edges into debounce or edge counters. At least 2 ms
       elapses after a bias change; a float classification needs two full pairs. */
    bool sample=(uint32_t)(now-s->switched_at)>=2u;
    for(unsigned i=0;i<3;i++) {
        uint8_t bit=(uint8_t)(1u<<i),mode=(s->config>>(3*i))&7u;
        if(mode==SC_BIAS_FLOAT) {
            if(sample && s->phase==1) {
                uint8_t state=(s->up_sample&bit)?((pins&bit)?SC_STATE_HIGH:SC_STATE_FLOAT):
                                                   ((pins&bit)?SC_STATE_UNKNOWN:SC_STATE_LOW);
                if(state!=s->candidate[i]){s->candidate[i]=state;s->repeats[i]=1;s->valid&=(uint8_t)~bit;}
                else if(s->repeats[i]<2)s->repeats[i]++;
                if(state==SC_STATE_UNKNOWN){s->state[i]=state;s->valid&=(uint8_t)~bit;}
                else if(s->repeats[i]>=2){s->state[i]=state;s->valid|=bit;}
            }
        } else if(sample || (s->valid&bit)) {
            s->state[i]=(pins&bit)?SC_STATE_HIGH:SC_STATE_LOW;s->valid|=bit;
            if(mode==SC_BIAS_KEEPER)s->keeper=(s->keeper&~bit)|(pins&bit);
        }
    }
    if(sample) {
        if(s->phase==0)s->up_sample=pins;
        s->phase^=1;s->switched_at=now;
    }
    s->high=s->floating=s->logical=0;
    for(unsigned i=0;i<3;i++) {
        uint8_t bit=(uint8_t)(1u<<i),state=s->state[i];
        if(state==SC_STATE_HIGH)s->high|=bit;
        if(state==SC_STATE_FLOAT)s->floating|=bit;
        if(!(s->valid&bit))continue;
        bool active=false;
        switch((s->config>>(9+3*i))&7u) {
        case SC_ACTIVE_HIGH:active=state==SC_STATE_HIGH;break;
        case SC_ACTIVE_LOW:active=state==SC_STATE_LOW;break;
        case SC_ACTIVE_DRIVEN:active=state!=SC_STATE_FLOAT;break;
        case SC_ACTIVE_FLOAT:active=state==SC_STATE_FLOAT;break;
        case SC_ACTIVE_NOT_HIGH:active=state!=SC_STATE_HIGH;break;
        case SC_ACTIVE_NOT_LOW:active=state!=SC_STATE_LOW;break;
        }
        if(active)s->logical|=bit;
    }
    drive(s);
}
