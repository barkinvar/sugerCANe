#include "sensor_core.h"
#include <stddef.h>
#include <string.h>
_Static_assert(sizeof(sc_config_record) == 32, "Flash record size");
_Static_assert(offsetof(sc_config_record, crc) == 24, "Flash CRC offset");
_Static_assert(offsetof(sc_config_record, commit) == 28, "Commit is written last");
uint32_t sc_crc32(const void *data, uint32_t length) {
    const uint8_t *p = data;
    uint32_t crc = 0xffffffffu;
    while (length--) {
        crc ^= *p++;
        for (unsigned i = 0; i < 8; i++)
            crc = (crc >> 1) ^ ((0u - (crc & 1u)) & 0xedb88320u);
    }
    return ~crc;
}
bool sc_config_valid(const sc_config_record *r) {
    return r->magic == SC_CONFIG_MAGIC && r->version == 1 && r->device_id < 64 &&
           r->invert_mask < 16 && r->debounce_ms >= 1 && r->debounce_ms <= 100 &&
           r->rail_mask < 4 && r->reserved0 == 0 && r->reserved1 == 0 && r->reserved2 == 0 &&
           r->commit == SC_CONFIG_COMMIT && r->crc == sc_crc32(r, 24);
}
int sc_config_newest(const sc_config_record *a, const sc_config_record *b) {
    bool av = sc_config_valid(a), bv = sc_config_valid(b);
    if (!av && !bv)
        return -1;
    if (!av)
        return 1;
    if (!bv)
        return 0;
    /* Serial-number comparison handles sequence rollover without signed casts. */
    uint32_t d = b->sequence - a->sequence;
    return d != 0 && d < 0x80000000u ? 1 : 0;
}
void sc_inputs_init(sc_inputs *s, uint8_t raw, uint8_t invert, uint16_t debounce, uint32_t now) {
    memset(s, 0, sizeof(*s));
    s->invert = invert & 15;
    s->debounce_ms = debounce;
    s->raw = raw & 15;
    s->candidate = s->stable = (raw ^ s->invert) & 15;
    for (unsigned i = 0; i < 4; i++)
        s->changed_at[i] = now;
    s->initialized = true;
}
void sc_inputs_update(sc_inputs *s, uint8_t raw, uint32_t now) {
    s->raw = raw & 15;
    uint8_t logical = (s->raw ^ s->invert) & 15;
    for (unsigned i = 0; i < 4; i++) {
        uint8_t bit = (uint8_t)(1u << i);
        if ((logical ^ s->candidate) & bit) {
            s->candidate ^= bit;
            s->changed_at[i] = now;
        }
        if (((s->candidate ^ s->stable) & bit) &&
            (uint32_t)(now - s->changed_at[i]) >= s->debounce_ms) {
            s->stable ^= bit;
            if (s->stable & bit)
                s->rising[i]++;
        }
    }
}
uint8_t sc_power_faults(uint8_t raw_faults, bool adc_ok, uint16_t battery_mv, uint16_t sensor5_mv) {
    /* TPS1H200A FAULT also asserts for healthy loads below 10-20mA. Its
       autonomous current-limit/latch protection remains active. Judge battery
       delivery from the switched-output ADC, not that ambiguous digital pin.
       The 5V switch has no such open-load report. Startup blanking is below. */
    if (!adc_ok)
        return 3;
    return (uint8_t)((raw_faults & 1u) | (sensor5_mv < 4500 ? 1u : 0u) |
                     (battery_mv < 4500 ? 2u : 0u));
}
void sc_rails_init(sc_rails *s, uint8_t requested, bool watchdog_reset, uint32_t now) {
    memset(s, 0, sizeof(*s));
    s->requested = requested & 3;
    /* A crashed foreground/clock must not repeatedly power-cycle a connected sensor. */
    if (watchdog_reset)
        s->latched = 3;
    s->disabled_at[0] = s->disabled_at[1] = now;
}
void sc_rails_update(sc_rails *s, uint8_t fault_low, uint32_t now) {
    for (unsigned i = 0; i < 2; i++) {
        uint8_t bit = (uint8_t)(1u << i);
        /* Hardware current limiting remains active during this 5ms startup interval. */
        if ((s->enabled & fault_low & bit) && (uint32_t)(now - s->enabled_at[i]) >= 5)
            s->latched |= bit;
        bool want = (s->requested & bit) && !(s->latched & bit);
        if (want && !(s->enabled & bit)) {
            s->enabled |= bit;
            s->enabled_at[i] = now;
        }
        if (!want && (s->enabled & bit)) {
            s->enabled &= (uint8_t)~bit;
            s->disabled_at[i] = now;
        }
    }
}
void sc_rails_emergency_off(sc_rails *s, uint32_t now) {
    s->requested = s->enabled = 0;
    s->latched = 3;
    s->disabled_at[0] = s->disabled_at[1] = now;
}
bool sc_rails_clear(sc_rails *s, uint8_t mask, uint32_t now) {
    if (mask == 0 || mask > 3)
        return false;
    for (unsigned i = 0; i < 2; i++)
        if ((mask & (1u << i)) &&
            ((s->enabled & (1u << i)) || (uint32_t)(now - s->disabled_at[i]) < 100))
            return false;
    s->latched &= (uint8_t)~mask;
    return true;
}
uint32_t sc_can_id(uint8_t device, uint16_t api) {
    return (SC_DEVICE_TYPE << 24) | (SC_MANUFACTURER << 16) | ((uint32_t)(api & 1023) << 6) |
           (device & 63);
}
bool sc_can_is_ours(uint32_t id, uint8_t device) {
    return (id & 0x1fff003fu) == sc_can_id(device, 0);
}
void sc_put_u16(uint8_t *p, uint16_t n) {
    p[0] = (uint8_t)n;
    p[1] = (uint8_t)(n >> 8);
}
void sc_put_u32(uint8_t *p, uint32_t n) {
    for (unsigned i = 0; i < 4; i++)
        p[i] = (uint8_t)(n >> (8 * i));
}
