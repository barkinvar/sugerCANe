#ifndef SC_INPUT_MODE_H
#define SC_INPUT_MODE_H
#include <stdbool.h>
#include <stdint.h>
enum { SC_BIAS_OFF, SC_BIAS_UP, SC_BIAS_DOWN, SC_BIAS_FLOAT, SC_BIAS_KEEPER };
enum { SC_ACTIVE_HIGH, SC_ACTIVE_LOW, SC_ACTIVE_DRIVEN, SC_ACTIVE_FLOAT,
       SC_ACTIVE_NOT_HIGH, SC_ACTIVE_NOT_LOW };
enum { SC_STATE_LOW, SC_STATE_HIGH, SC_STATE_FLOAT, SC_STATE_UNKNOWN };
typedef struct {
    uint32_t config, switched_at;
    uint8_t state[3], candidate[3], repeats[3], keeper, up_sample, phase;
    uint8_t up, down, valid, logical, high, floating;
} sc_input_modes;
bool sc_input_config_valid(uint32_t config);
void sc_input_modes_init(sc_input_modes *, uint32_t config, uint32_t now);
void sc_input_modes_update(sc_input_modes *, uint8_t pins, uint32_t now);
#endif
