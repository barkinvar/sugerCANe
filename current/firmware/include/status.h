#ifndef SC_STATUS_H
#define SC_STATUS_H
#include <stdint.h>
typedef enum {
    SC_LED_READY, SC_LED_WAIT, SC_LED_POWER_FAULT, SC_LED_CAN_ERROR,
    SC_LED_BOOT, SC_LED_IDENTIFY
} sc_led_state;
uint32_t sc_status_color(sc_led_state state, uint32_t now);
#endif
