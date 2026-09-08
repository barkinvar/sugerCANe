#include "board.h"
#include "board_service.h"
static sc_service service;
#include <string.h>
static sc_inputs inputs;
static sc_input_modes modes;
static uint8_t input_ready;
static uint8_t device_id, status_sequence, reset_flags;
static bool configured, clock_ok, can_ok, telemetry_enabled = true;
static uint8_t rail_good;
static uint32_t rail_good_since[2];
static uint32_t tx_dropped;
/* Faults invalidate immediately. Recovery needs 100 ms continuously healthy;
   robot code must add any longer startup delay specified by its sensor. */
static void power_status(uint32_t now) {
    uint8_t pins=(uint8_t)((GPIOA->IDR >> 3) & 3u);
    for (unsigned i=0;i<2;i++) {
        uint8_t mask=(uint8_t)(1u<<i);
        if (!(pins & mask)) { rail_good &= (uint8_t)~mask; rail_good_since[i]=now; }
        else if ((uint32_t)(now-rail_good_since[i])>=100u) rail_good |= mask;
    }
}
static void send_frame(uint16_t api, const uint8_t data[8]) {
    if (configured && can_ok && telemetry_enabled && !sc_service_active(&service) && !board_can_send(sc_can_id(device_id, api), data))
        tx_dropped++;
}
static void status_frame(void) {
    uint8_t d[8] = {SC_PROTOCOL_VERSION,
                    status_sequence++,
                    inputs.stable,
                    inputs.raw,
                    3, /* Physical channel count, never a power-state report. */
                    0x7f, /* Includes configurable bias and input-state telemetry. */
                    (uint8_t)((configured ? 1 : 0) | (clock_ok ? 2 : 0) | (can_ok ? 4 : 0) | ((CAN->ESR & CAN_ESR_BOFF) ? 8 : 0) | (rail_good << 4) | ((modes.valid==7)?64:0)),
                    reset_flags};
    send_frame(SC_API_STATUS, d);
}
static void counters_frame(unsigned pair) {
    uint8_t d[8];
    sc_put_u32(d, inputs.rising[pair * 2]);
    sc_put_u32(d + 4, pair ? 0 : inputs.rising[1]);
    send_frame(pair ? SC_API_COUNTS34 : SC_API_COUNTS12, d);
}
static void diagnostic_frame(void) {
    uint8_t d[8];
    sc_put_u32(d, tx_dropped);
    d[4]=(uint8_t)(CAN->ESR>>16); d[5]=(uint8_t)(CAN->ESR>>24);
    d[6]=(uint8_t)((CAN->ESR>>4)&7u);
    d[7]=(uint8_t)(((CAN->ESR & CAN_ESR_BOFF)?1:0)|((CAN->ESR & CAN_ESR_EPVF)?2:0));
    send_frame(SC_API_DIAGNOSTIC,d);
}
static void identity_frame(void) {
    uint8_t d[8] = {SC_PROTOCOL_VERSION, 0, 6, 0, 5, device_id, (uint8_t)inputs.debounce_ms,
                    inputs.invert};
    send_frame(SC_API_IDENTITY, d);
}
static void apply_runtime(uint8_t invert, uint16_t debounce, uint32_t now) {
    uint32_t counts[3];
    memcpy(counts, inputs.rising, sizeof(counts));
    sc_inputs_init(&inputs, modes.logical, invert & 7u, debounce, now);
    inputs.raw=modes.high;
    memcpy(inputs.rising, counts, sizeof(counts));
}
static void input_state_frame(void) {
    uint8_t d[8]={SC_PROTOCOL_VERSION,modes.valid,modes.floating,modes.high,0,0,0,0};
    sc_put_u32(d+4,modes.config);send_frame(SC_API_INPUT_STATE,d);
}
static void update_inputs(uint32_t now,bool allowed) {
    sc_input_modes_update(&modes,(uint8_t)GPIOA->IDR,now);
    board_bias(modes.up,modes.down);
    if(!allowed){input_ready=0;apply_runtime(inputs.invert,inputs.debounce_ms,now);return;}
    uint8_t logical=(modes.logical^inputs.invert)&7u;
    for(unsigned i=0;i<3;i++) {
        uint8_t bit=(uint8_t)(1u<<i);
        if(!(modes.valid&bit)) {
            inputs.candidate=(inputs.candidate&~bit)|(inputs.stable&bit);
            inputs.changed_at[i]=now;
        } else if(!(input_ready&bit)) {
            inputs.candidate=(inputs.candidate&~bit)|(logical&bit);
            inputs.stable=(inputs.stable&~bit)|(logical&bit);
            inputs.changed_at[i]=now;
        }
    }
    /* Substitute the stable state for invalid channels before debounce. */
    uint8_t sample=(modes.logical&modes.valid)|((inputs.stable^inputs.invert)&~modes.valid&7u);
    sc_inputs_update(&inputs,sample,now);inputs.raw=modes.high;input_ready|=modes.valid;
}
static void receive_commands(uint32_t now) {
    /* Bound work even under an intentional or accidental receive flood. */
    for (unsigned k = 0; k < 3; k++) {
        uint32_t id;
        uint8_t d[8], len;
        if (!board_can_receive(&id, d, &len))
            break;
        if (id == 0) {
            /* Immediately stop telemetry and abort pending transmit mailboxes.
               No actuator outputs exist. Sensor power is independent hardware. */
            telemetry_enabled=false;
            sc_service_disable(&service);
            board_can_abort();
            return;
        }
        if (id==SC_SERVICE_RX && len==8) {sc_service_receive(&service,d,now);continue;}
        if (sc_service_active(&service) || !configured)continue;
        if (len != 8 || !sc_can_is_ours(id, device_id) || d[0] != 0x53 || d[1] != 0x43 ||
            d[2] != SC_PROTOCOL_VERSION)
            continue;
        uint16_t api = (uint16_t)((id >> 6) & 1023u);
        if (api == SC_API_CONFIG) {
            uint16_t db = (uint16_t)(d[4] | ((uint16_t)d[5] << 8));
            if (d[3] < 8 && db >= 1 && db <= 100 && d[6] == 0 && d[7] == 0)
                apply_runtime(d[3], db, now);
        } else if (api == SC_API_INPUT_CONFIG && d[3]==0 && sc_input_config_valid(sc_get_u32(d+4))) {
            sc_input_modes_init(&modes,sc_get_u32(d+4),now);input_ready=0;
            board_bias(modes.up,modes.down);
        } else if (api == SC_API_RESUME && d[3]==0 && d[4]==0 && d[5]==0 && d[6]==0 && d[7]==0) {
            telemetry_enabled=true;
        }
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
    board_uart_write("SC12 v0.6.0 proto=4 configured=");
    uart_uint(configured);
    board_uart_write(" id=");
    uart_uint(device_id);
    board_uart_write(" invert=");
    uart_uint(inputs.invert);
    board_uart_write(" debounce_ms=");
    uart_uint(inputs.debounce_ms);
    board_uart_write(" telemetry=");
    uart_uint(telemetry_enabled);
    board_uart_write(" clock_ok=");
    uart_uint(clock_ok);
    board_uart_write(" can_ok=");
    uart_uint(can_ok);
    board_uart_write(" rail12_pg=");
    uart_uint((rail_good & 1u)!=0);
    board_uart_write(" rail5_no_fault=");
    uart_uint((rail_good & 2u)!=0);
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
static void uart_command(const char *line) {
    if (!strcmp(line, "INFO")) {
        print_status();
        return;
    }
    if (!strcmp(line, "RESUME")) {telemetry_enabled=true;board_uart_write("OK\r\n");return;}
    if (!strcmp(line, "HELP")) {
        board_uart_write(
            "INFO | SET id invert debounce_ms | RESUME | HELP\r\n"
            "SET persists and resets. id0..63 invert0..7 debounce1..100. Power is hardware-only.\r\n");
        return;
    }
    uint32_t n[3];
    if (!strncmp(line, "SET ", 4) && parse_numbers(line + 4, n, 3) && n[0] < 64 && n[1] < 8 &&
        n[2] >= 1 && n[2] <= 100) {
        sc_config_record r = {0};
        r.device_id = (uint8_t)n[0];
        r.invert_mask = (uint8_t)n[1];
        r.debounce_ms = (uint16_t)n[2];
        r.input_config=modes.config;
        bool ok = board_config_store(&r);
        board_uart_write(ok ? "OK: saved; resetting\r\n" : "ERR: flash; resetting safely\r\n");
        board_uart_flush();
        NVIC_SystemReset();
    }
    board_uart_write("ERR: HELP for syntax\r\n");
}
static void uart_poll(void) {
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
                uart_command(line);
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
    sc_input_modes_init(&modes,cfg?cfg->input_config:0,0);
    board_bias(modes.up,modes.down);
    sc_inputs_init(&inputs, 0, cfg ? (cfg->invert_mask & 7u) : 0,
                   cfg ? cfg->debounce_ms : 2, 0);
    board_service_init(&service,false);
    can_ok = clock_ok && board_can_init(device_id);
    if (can_ok)
        board_can_standby(false);
    board_uart_write("FRC Sensor CAN SC12 prototype v0.6.0\r\n");
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
            bool previously_powered=rail_good==3;
            power_status(now);
            update_inputs(now,rail_good==3 && previously_powered && !sc_service_active(&service));
            bool error=!clock_ok || !configured || !can_ok || rail_good!=3 || (CAN->ESR & CAN_ESR_BOFF);
            sc_service_tick(&service,now);
            if(now>=2000)board_boot_healthy();
            board_status_led(service.blink_until && (uint32_t)(service.blink_until-now)<0x80000000u ? now%100<50 : error ? ((now%200)<100) : ((now%1000)<100));
            if (can_ok)
                receive_commands(now);
            uart_poll();
            if ((uint32_t)(now - next_status) < 0x80000000u) {
                next_status = now + service.period;
                status_frame();
                input_state_frame();
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
