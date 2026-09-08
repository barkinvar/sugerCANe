#include "sensor_core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void seal(sc_config_record *r) {r->magic=SC_CONFIG_MAGIC;r->version=SC_PROTOCOL_VERSION;r->commit=SC_CONFIG_COMMIT;r->crc=sc_crc32(r,24);}
int main(void) {
    assert(sc_crc32("123456789",9)==0xcbf43926u);
    sc_config_record a={.device_id=63,.invert_mask=7,.debounce_ms=2,.sequence=0xffffffffu};
    seal(&a);assert(sc_config_valid(&a));
    sc_config_record b=a;b.sequence=0;seal(&b);assert(sc_config_newest(&a,&b)==1);
    b.commit=0;assert(sc_config_newest(&a,&b)==0);
    b=a;b.version=1;b.crc=sc_crc32(&b,24);assert(!sc_config_valid(&b));
    b=a;b.invert_mask=8;seal(&b);assert(!sc_config_valid(&b));
    b=a;b.reserved_power=1;seal(&b);assert(!sc_config_valid(&b));
    b=a;b.debounce_ms=0;seal(&b);assert(!sc_config_valid(&b));
    b=a;b.debounce_ms=101;seal(&b);assert(!sc_config_valid(&b));
    for (unsigned i=0;i<32;i++) {b=a;((unsigned char*)&b)[i]^=1;assert(!sc_config_valid(&b));}
    sc_inputs s;sc_inputs_init(&s,0,0,3,0xfffffffeu);
    sc_inputs_update(&s,1,0xffffffffu);sc_inputs_update(&s,1,0);assert(s.stable==0);
    sc_inputs_update(&s,1,2);assert(s.stable==1 && s.rising[0]==1);
    sc_inputs_update(&s,0,3);sc_inputs_update(&s,1,4);sc_inputs_update(&s,1,7);assert(s.rising[0]==1);
    sc_inputs_update(&s,0,8);sc_inputs_update(&s,0,11);assert(s.stable==0);
    sc_inputs_update(&s,7,12);sc_inputs_update(&s,7,15);assert(s.stable==7 && s.rising[0]==2 && s.rising[1]==1 && s.rising[2]==1);
    s.rising[2]=0xffffffffu;sc_inputs_update(&s,3,16);sc_inputs_update(&s,3,19);sc_inputs_update(&s,7,20);sc_inputs_update(&s,7,23);assert(s.rising[2]==0);
    sc_inputs_init(&s,255,255,2,0);assert(s.raw==7 && s.stable==0 && s.invert==7);
    uint8_t bytes[6]={0xab,0,0,0,0,0xcd};sc_put_u32(bytes+1,0x87654321);assert(bytes[0]==0xab&&bytes[1]==0x21&&bytes[4]==0x87&&bytes[5]==0xcd);
    assert(sc_can_id(17,0x120)==0x0a084811u);
    assert(sc_can_is_ours(sc_can_id(17,0x220),17));assert(!sc_can_is_ours(sc_can_id(18,0x220),17));
    puts("core: CRC, torn records, version/range rejection, rollover, debounce, inversion, count overflow, wire encoding passed");
}
