#ifndef SC_POWER_H
#define SC_POWER_H
#include <stdint.h>
#include <stdbool.h>
/* Bit 0 = 12 V, bit 1 = 5 V; matches status telemetry. */
typedef struct {
    uint8_t enabled, good, latched, pending;
    uint16_t mv[2];
    uint32_t requested[2], started[2], healthy_since[2], bad_since[2];
    bool available;
} sc_power;
extern sc_power sensor_power;
void sc_power_init(sc_power *,uint32_t now,bool available);
void sc_power_restart(sc_power *,uint8_t mask,uint32_t now);
void sc_power_update(sc_power *,uint32_t now,bool valid,uint16_t mv12,uint16_t mv5,uint8_t fault);
#endif
