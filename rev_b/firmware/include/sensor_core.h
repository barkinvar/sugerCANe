#ifndef SENSOR_CORE_H
#define SENSOR_CORE_H
#include <stdbool.h>
#include <stdint.h>
#define SC_PROTOCOL_VERSION 1u
#define SC_DEVICE_TYPE 10u
#define SC_MANUFACTURER 8u
#define SC_API_STATUS 0x100u
#define SC_API_COUNTS12 0x101u
#define SC_API_COUNTS34 0x102u
#define SC_API_DIAGNOSTIC 0x110u
#define SC_API_IDENTITY 0x111u
#define SC_API_CONFIG 0x200u
#define SC_API_CLEAR_FAULT 0x201u
#define SC_CONFIG_MAGIC 0x53434e31u
#define SC_CONFIG_COMMIT 0xc0dec0deu
/* Byte layout is fixed, little endian, with CRC over bytes [0,24). */
typedef struct {
    uint32_t magic, sequence;
    uint16_t version;
    uint8_t device_id, invert_mask;
    uint16_t debounce_ms;
    uint8_t rail_mask, reserved0;
    uint32_t reserved1, reserved2, crc, commit;
} sc_config_record;
typedef struct {
    uint32_t changed_at[4], rising[4];
    uint8_t raw, candidate, stable, invert;
    uint16_t debounce_ms;
    bool initialized;
} sc_inputs;
typedef struct {
    uint8_t requested, enabled, latched;
    uint32_t enabled_at[2], disabled_at[2];
} sc_rails;
uint32_t sc_crc32(const void *data, uint32_t length);
bool sc_config_valid(const sc_config_record *r);
int sc_config_newest(const sc_config_record *a, const sc_config_record *b);
void sc_inputs_init(sc_inputs *s, uint8_t raw, uint8_t invert, uint16_t debounce, uint32_t now);
void sc_inputs_update(sc_inputs *s, uint8_t raw, uint32_t now);
void sc_rails_update(sc_rails *s, uint8_t fault_low, uint32_t now);
uint8_t sc_power_faults(uint8_t raw_faults, bool adc_ok, uint16_t battery_mv, uint16_t sensor5_mv);
void sc_rails_init(sc_rails *s, uint8_t requested, bool watchdog_reset, uint32_t now);
void sc_rails_emergency_off(sc_rails *s, uint32_t now);
bool sc_rails_clear(sc_rails *s, uint8_t mask, uint32_t now);
uint32_t sc_can_id(uint8_t device, uint16_t api);
bool sc_can_is_ours(uint32_t id, uint8_t device);
void sc_put_u16(uint8_t *p, uint16_t n);
void sc_put_u32(uint8_t *p, uint32_t n);
#endif
