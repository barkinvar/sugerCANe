#include "status.h"
/* RGB bytes; modest brightness for a case window. Patterns also distinguish
 * conditions without relying solely on color perception. */
uint32_t sc_status_color(sc_led_state state, uint32_t now) {
    switch (state) {
    case SC_LED_READY: return now%1000u<100u ? 0x006000u : 0;
    case SC_LED_WAIT: return now%1000u<100u ? 0x604000u : 0;
    case SC_LED_POWER_FAULT:
        now%=1000u;
        return now<100u || (now>=200u && now<300u) ? 0x800000u : 0;
    case SC_LED_CAN_ERROR: return now%500u<250u ? 0x800000u : 0;
    case SC_LED_BOOT: return now%1000u<200u ? 0x000080u : 0;
    case SC_LED_IDENTIFY: return now%100u<50u ? 0x600060u : 0;
    }
    return 0;
}
