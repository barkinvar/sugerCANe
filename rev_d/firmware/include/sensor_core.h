#ifndef SENSOR_CORE_H
#define SENSOR_CORE_H
#include <stdbool.h>
#include <stdint.h>
#define SC_PROTOCOL_VERSION 3u
#define SC_DEVICE_TYPE 10u
#define SC_MANUFACTURER 8u
#define SC_API_STATUS 0x120u
#define SC_API_COUNTS12 0x121u
#define SC_API_COUNTS34 0x122u
#define SC_API_DIAGNOSTIC 0x130u
#define SC_API_IDENTITY 0x131u
#define SC_API_CONFIG 0x220u
#define SC_API_RESUME 0x221u
#define SC_CONFIG_MAGIC 0x53434e32u
#define SC_CONFIG_COMMIT 0xc0dec0deu
/* Byte layout is fixed, little endian, with CRC over bytes [0,24). */
typedef struct {
    uint32_t magic, sequence;
    uint16_t version;
    uint8_t device_id, invert_mask;
    uint16_t debounce_ms;
    uint8_t reserved_power, reserved0;
    uint32_t reserved1, reserved2, crc, commit;
} sc_config_record;
typedef struct {
    uint32_t changed_at[3], rising[3];
    uint8_t raw, candidate, stable, invert;
    uint16_t debounce_ms;
    bool initialized;
} sc_inputs;
uint32_t sc_crc32(const void *data, uint32_t length);
bool sc_config_valid(const sc_config_record *r);
int sc_config_newest(const sc_config_record *a, const sc_config_record *b);
void sc_inputs_init(sc_inputs *s, uint8_t raw, uint8_t invert, uint16_t debounce, uint32_t now);
void sc_inputs_update(sc_inputs *s, uint8_t raw, uint32_t now);
uint32_t sc_can_id(uint8_t device, uint16_t api);
bool sc_can_is_ours(uint32_t id, uint8_t device);
void sc_put_u16(uint8_t *p, uint16_t n);
void sc_put_u32(uint8_t *p, uint32_t n);
#endif
