#include "board.h"
#include <string.h>
static sc_inputs inputs;
static sc_rails rails;
static uint8_t device_id, status_sequence, reset_flags;
static bool configured, clock_ok, adc_ok, adc_initialized, can_ok;
static uint16_t battery_mv, sensor_mv;
static uint32_t tx_dropped;
static void send_frame(uint16_t api, const uint8_t data[8]) {
    if (configured && can_ok && !board_can_send(sc_can_id(device_id, api), data))
        tx_dropped++;
}
static void status_frame(void) {
    uint8_t d[8] = {SC_PROTOCOL_VERSION,
                    status_sequence++,
                    inputs.stable,
                    inputs.raw,
                    rails.enabled,
                    rails.latched,
                    (uint8_t)((configured ? 1 : 0) | (clock_ok ? 2 : 0) | (adc_ok ? 4 : 0)),
                    reset_flags};
    send_frame(SC_API_STATUS, d);
}
static void counters_frame(unsigned pair) {
    uint8_t d[8];
    sc_put_u32(d, inputs.rising[pair * 2]);
    sc_put_u32(d + 4, inputs.rising[pair * 2 + 1]);
    send_frame(pair ? SC_API_COUNTS34 : SC_API_COUNTS12, d);
}
static void diagnostic_frame(void) {
    uint8_t d[8];
    sc_put_u16(d, battery_mv);
    sc_put_u16(d + 2, sensor_mv);
    sc_put_u16(d + 4, (uint16_t)(tx_dropped > 65535 ? 65535 : tx_dropped));
    d[6] = (uint8_t)(CAN->ESR >> 16);
    d[7] = (uint8_t)(CAN->ESR >> 24);
    send_frame(SC_API_DIAGNOSTIC, d);
}
static void identity_frame(void) {
    uint8_t d[8] = {SC_PROTOCOL_VERSION, 0, 1, 0, 1, device_id, (uint8_t)inputs.debounce_ms,
                    inputs.invert};
    send_frame(SC_API_IDENTITY, d);
}
static void apply_runtime(uint8_t invert, uint16_t debounce, uint8_t power, uint32_t now) {
    uint32_t counts[4];
    memcpy(counts, inputs.rising, sizeof(counts));
    sc_inputs_init(&inputs, (uint8_t)GPIOA->IDR, invert, debounce, now);
    memcpy(inputs.rising, counts, sizeof(counts));
    rails.requested = power;
}
static void receive_commands(uint32_t now) {
    /* Bound work even under an intentional or accidental receive flood. */
    for (unsigned k = 0; k < 3; k++) {
        uint32_t id;
        uint8_t d[8], len;
        if (!board_can_receive(&id, d, &len))
            break;
        if (id == 0) {
            /* Required FRC Broadcast Disable: no payload requirement. */
            board_set_rails(0);
            sc_rails_emergency_off(&rails, now);
            return;
        }
        if (len != 8 || !sc_can_is_ours(id, device_id) || d[0] != 0x53 || d[1] != 0x43 ||
            d[2] != SC_PROTOCOL_VERSION)
            continue;
        uint16_t api = (uint16_t)((id >> 6) & 1023u);
        if (api == SC_API_CONFIG) {
            uint16_t db = (uint16_t)(d[4] | ((uint16_t)d[5] << 8));
            if (d[3] < 16 && db >= 1 && db <= 100 && d[6] < 4 && d[7] == 0)
                apply_runtime(d[3], db, d[6], now);
        } else if (api == SC_API_CLEAR_FAULT && d[4] == 0 && d[5] == 0 && d[6] == 0 && d[7] == 0)
            sc_rails_clear(&rails, d[3], now);
    }
}
static void uart_uint(uint32_t n) {
    char b[11];
    unsigned i = sizeof(b) - 1;
    b[i] = 0;
    do {
        b[--i] = (char)('0' + n % 10);
        n /= 10;
    } while (n);
    board_uart_write(b + i);
}
static void print_status(void) {
    board_uart_write("SC v0.1.0 proto=1 configured=");
    uart_uint(configured);
    board_uart_write(" id=");
    uart_uint(device_id);
    board_uart_write(" invert=");
    uart_uint(inputs.invert);
    board_uart_write(" debounce_ms=");
    uart_uint(inputs.debounce_ms);
    board_uart_write(" rails=");
    uart_uint(rails.enabled);
    board_uart_write(" requested=");
    uart_uint(rails.requested);
    board_uart_write(" faults=");
    uart_uint(rails.latched);
    board_uart_write(" clock_ok=");
    uart_uint(clock_ok);
    board_uart_write(" can_ok=");
    uart_uint(can_ok);
    board_uart_write(" adc_ok=");
    uart_uint(adc_ok);
    board_uart_write(" sensorbat_mV=");
    uart_uint(battery_mv);
    board_uart_write(" sensor5_mV=");
    uart_uint(sensor_mv);
    board_uart_write("\r\n");
}
static bool parse_numbers(const char *s, uint32_t *out, unsigned count) {
    for (unsigned i = 0; i < count; i++) {
        while (*s == ' ')
            s++;
        if (*s < '0' || *s > '9')
            return false;
        uint32_t n = 0;
        while (*s >= '0' && *s <= '9') {
            if (n > 10000)
                return false;
            n = n * 10 + (uint32_t)(*s++ - '0');
        }
        out[i] = n;
    }
    while (*s == ' ')
        s++;
    return *s == 0;
}
static void uart_command(const char *line, uint32_t now) {
    if (!strcmp(line, "INFO")) {
        print_status();
        return;
    }
    if (!strcmp(line, "HELP")) {
        board_uart_write(
            "INFO | SET id invert debounce_ms rails | CLEAR mask | HELP\r\nSET persists and "
            "resets. id0..63 invert0..15 debounce1..100 rails0..3; rail bits 1=5V 2=VBAT.\r\n");
        return;
    }
    uint32_t n[4];
    if (!strncmp(line, "CLEAR ", 6) && parse_numbers(line + 6, n, 1)) {
        board_uart_write(n[0] <= 3 && sc_rails_clear(&rails, (uint8_t)n[0], now)
                             ? "OK\r\n"
                             : "ERR: off time/mask\r\n");
        return;
    }
    if (!strncmp(line, "SET ", 4) && parse_numbers(line + 4, n, 4) && n[0] < 64 && n[1] < 16 &&
        n[2] >= 1 && n[2] <= 100 && n[3] < 4) {
        sc_config_record r = {0};
        r.device_id = (uint8_t)n[0];
        r.invert_mask = (uint8_t)n[1];
        r.debounce_ms = (uint16_t)n[2];
        r.rail_mask = (uint8_t)n[3];
        bool ok = board_config_store(&r);
        board_uart_write(ok ? "OK: saved; resetting\r\n" : "ERR: flash; resetting safely\r\n");
        board_uart_flush();
        NVIC_SystemReset();
    }
    board_uart_write("ERR: HELP for syntax\r\n");
}
static void uart_poll(uint32_t now) {
    static char line[64];
    static unsigned used;
    static bool overflow;
    /* UART input is bounded; no dynamic allocation and no blocking receive. */
    for (unsigned k = 0; k < 8; k++) {
        int c = board_uart_get();
        if (c == -1)
            break;
        if (c == -2) {
            overflow = true;
            continue;
        }
        if (c == '\r' || c == '\n') {
            if (overflow)
                board_uart_write("ERR: serial line discarded\r\n");
            else if (used) {
                line[used] = 0;
                uart_command(line, now);
            }
            used = 0;
            overflow = false;
        } else if (c >= 32 && c <= 126) {
            if (used < sizeof(line) - 1)
                line[used++] = (char)c;
            else
                overflow = true;
        } else {
            overflow = true;
        }
    }
}
int main(void) {
    board_gpio_init();
    uint32_t csr = RCC->CSR;
    reset_flags = (uint8_t)(((csr & RCC_CSR_PORRSTF) ? 1 : 0) | ((csr & RCC_CSR_PINRSTF) ? 2 : 0) |
                            ((csr & RCC_CSR_IWDGRSTF) ? 4 : 0) | ((csr & RCC_CSR_SFTRSTF) ? 8 : 0));
    RCC->CSR |= RCC_CSR_RMVF;
    board_watchdog_start();
    board_voltage_guard_init();
    clock_ok = board_clock_init();
    SysTick_Config(SystemCoreClock / 1000u);
    board_uart_init();
    const sc_config_record *cfg = board_config_load();
    configured = cfg != 0;
    device_id = cfg ? cfg->device_id : 0;
    sc_inputs_init(&inputs, (uint8_t)GPIOA->IDR, cfg ? cfg->invert_mask : 0,
                   cfg ? cfg->debounce_ms : 2, 0);
    sc_rails_init(&rails, clock_ok && cfg ? cfg->rail_mask : 0, (reset_flags & 4) != 0,
                  board_millis);
    adc_ok = adc_initialized = board_adc_init();
    can_ok = clock_ok && configured && board_can_init(device_id);
    if (can_ok)
        board_can_standby(false);
    board_uart_write("FRC Sensor CAN prototype v0.1.0\r\n");
    print_status();
    uint32_t last_tick = board_millis, next_status = last_tick + 10,
             next_counts12 = last_tick + 100, next_counts34 = last_tick + 125,
             next_diag = last_tick + 150, next_identity = last_tick + 1000;
    for (;;) {
        uint32_t now = board_millis;
        if (now != last_tick) {
            uint32_t elapsed = now - last_tick;
            last_tick = now;
            /* Missed >20ms indicates a stalled foreground task: force safe reset. */
            if (elapsed > 20) {
                board_safe_off();
                for (;;) {
                }
            }
            sc_inputs_update(&inputs, (uint8_t)GPIOA->IDR, now);
            /* Three 239.5-cycle ADC samples take about54us at14MHz. Read each
               1ms tick so startup blanking and output-loss detection use fresh
               measurements. CAN diagnostics still transmit only every100ms. */
            adc_ok = adc_initialized && board_adc_millivolts(&battery_mv, &sensor_mv);
            sc_rails_update(&rails, sc_power_faults(board_faults(), adc_ok, battery_mv, sensor_mv),
                            now);
            board_set_rails(rails.enabled);
            board_leds(inputs.stable, can_ok && ((now % 1000) < 100),
                       !clock_ok || !configured || !can_ok || rails.latched || !adc_ok);
            if (can_ok)
                receive_commands(now);
            uart_poll(now);
            if ((uint32_t)(now - next_status) < 0x80000000u) {
                next_status = now + 10;
                status_frame();
            }
            if ((uint32_t)(now - next_counts12) < 0x80000000u) {
                next_counts12 = now + 100;
                counters_frame(0);
            }
            if ((uint32_t)(now - next_counts34) < 0x80000000u) {
                next_counts34 = now + 100;
                counters_frame(1);
            }
            if ((uint32_t)(now - next_diag) < 0x80000000u) {
                next_diag = now + 100;
                if (can_ok)
                    diagnostic_frame();
            }
            if ((uint32_t)(now - next_identity) < 0x80000000u) {
                next_identity = now + 1000;
                identity_frame();
            }
            board_watchdog_feed(); /* Only after a complete scheduler iteration. */
        }
        __WFI();
    }
}
