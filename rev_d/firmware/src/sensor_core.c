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
    return r->magic == SC_CONFIG_MAGIC && r->version == SC_PROTOCOL_VERSION && r->device_id < 64 &&
           r->invert_mask < 8 && r->debounce_ms >= 1 && r->debounce_ms <= 100 &&
           r->reserved_power == 0 && r->reserved0 == 0 && r->reserved1 == 0 && r->reserved2 == 0 &&
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
    s->invert = invert & 7;
    s->debounce_ms = debounce;
    s->raw = raw & 7;
    s->candidate = s->stable = (raw ^ s->invert) & 7;
    for (unsigned i = 0; i < 3; i++)
        s->changed_at[i] = now;
    s->initialized = true;
}
void sc_inputs_update(sc_inputs *s, uint8_t raw, uint32_t now) {
    s->raw = raw & 7;
    uint8_t logical = (s->raw ^ s->invert) & 7;
    for (unsigned i = 0; i < 3; i++) {
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
