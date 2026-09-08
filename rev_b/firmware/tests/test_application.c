#include "board.h"
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int firmware_main(void);
host_gpio host_gpioa = {.IDR = 1};
host_rcc host_rcc_state = {.CSR = RCC_CSR_PORRSTF};
host_can host_can_state;
volatile uint32_t board_millis;
uint32_t SystemCoreClock = 48000000;
static jmp_buf done;
static const char *scenario;
static unsigned checks, feeds, can_inits, stores, resets, stops, sent_count;
static uint8_t physical_rails, output_at[501], fault;
static bool standby = true, red_at[501];
static char serial_out[16384];
static const char *serial_in = "";
static size_t serial_pos;
static sc_config_record config = {.device_id = 17,
                                  .invert_mask = 1,
                                  .debounce_ms = 2,
                                  .rail_mask = 3},
                        saved;
typedef struct {
    uint32_t at, id;
    uint8_t len, data[8];
} frame;
static frame pending[32], sent[128];
static unsigned pending_count, pending_pos;
#define CHECK(x)                                                                                   \
    do {                                                                                           \
        assert(x);                                                                                 \
        checks++;                                                                                  \
    } while (0)
static bool is(const char *name) {
    return !strcmp(scenario, name);
}
static void command(uint32_t at, uint16_t api, uint8_t a, uint16_t b, uint8_t c) {
    frame *f = &pending[pending_count++];
    f->at = at;
    f->id = sc_can_id(17, api);
    f->len = 8;
    f->data[0] = 0x53;
    f->data[1] = 0x43;
    f->data[2] = 1;
    f->data[3] = a;
    f->data[4] = (uint8_t)b;
    f->data[5] = (uint8_t)(b >> 8);
    f->data[6] = c;
}
void board_gpio_init(void) {
    physical_rails = 0;
    standby = true;
}
void board_voltage_guard_init(void) {}
bool board_clock_init(void) {
    return !is("clock_failure");
}
int SysTick_Config(uint32_t ticks) {
    CHECK(ticks == 48000);
    return 0;
}
void board_uart_init(void) {}
void board_watchdog_start(void) {}
void board_watchdog_feed(void) {
    feeds++;
}
void board_uart_write(const char *s) {
    CHECK(strlen(serial_out) + strlen(s) < sizeof(serial_out));
    strcat(serial_out, s);
}
int board_uart_get(void) {
    if (board_millis < 50 || !serial_in[serial_pos])
        return -1;
    return (unsigned char)serial_in[serial_pos++];
}
void board_uart_flush(void) {}
const sc_config_record *board_config_load(void) {
    return is("unconfigured") ? NULL : &config;
}
bool board_config_store(sc_config_record *r) {
    saved = *r;
    stores++;
    return true;
}
_Noreturn void NVIC_SystemReset(void) {
    resets++;
    longjmp(done, 2);
}
void board_can_standby(bool value) {
    standby = value;
}
bool board_can_init(uint8_t id) {
    CHECK(id == 17);
    can_inits++;
    return !is("can_init_failure");
}
bool board_can_send(uint32_t id, const uint8_t d[8]) {
    CHECK(!standby);
    CHECK(sent_count < 128);
    sent[sent_count] = (frame){.at = board_millis, .id = id, .len = 8};
    memcpy(sent[sent_count++].data, d, 8);
    return !is("can_busy");
}
bool board_can_receive(uint32_t *id, uint8_t d[8], uint8_t *len) {
    if (pending_pos == pending_count || pending[pending_pos].at > board_millis)
        return false;
    frame *f = &pending[pending_pos++];
    *id = f->id;
    *len = f->len;
    memcpy(d, f->data, 8);
    return true;
}
void board_set_rails(uint8_t mask) {
    CHECK(mask < 4);
    physical_rails = mask;
}
uint8_t board_faults(void) {
    return fault;
}
void board_leds(uint8_t inputs, bool green, bool red) {
    (void)green;
    CHECK(inputs < 8);
    if (board_millis <= 500)
        red_at[board_millis] = red;
}
bool board_adc_init(void) {
    return !is("adc_failure");
}
bool board_adc_millivolts(uint16_t *a, uint16_t *b) {
    if (is("adc_failure") || (is("adc_runtime_failure") && board_millis >= 20))
        return false;
    *a = physical_rails & 2 ? 12000 : 0;
    if ((is("battery_short") || is("battery_voltage_loss")) && board_millis >= 20 &&
        board_millis < 100)
        *a = is("battery_short") ? 0 : 4499;
    if (is("startup_ramp") && board_millis < 5)
        *a = 3000;
    if (is("startup_timeout"))
        *a = 4400;
    *b = physical_rails & 1 ? 4970 : 0;
    return true;
}
void board_safe_off(void) {
    physical_rails = 0;
    standby = true;
    stops++;
    if (is("scheduler_stall"))
        longjmp(done, 3);
}
void host_wait(void) {
    if (board_millis <= 500)
        output_at[board_millis] = physical_rails;
    if (board_millis >= 400)
        longjmp(done, 1);
    if (is("scheduler_stall") && board_millis == 49)
        board_millis += 21;
    else
        board_millis++;
    if (board_millis == 100)
        host_gpioa.IDR = 0;
    if (is("reserved_channel")) host_gpioa.IDR = (host_gpioa.IDR & 7u) | ((board_millis & 1u) << 3);
    if (is("fault_disable_recovery")) {
        if (board_millis == 20)
            fault = 1;
        if (board_millis == 100)
            fault = 0;
    }
    if (is("battery_open_load"))
        fault = 2;
    if (is("battery_short"))
        fault = board_millis >= 20 && board_millis < 100 ? 2 : 0;
}
static const frame *last_api(uint16_t api) {
    for (unsigned i = sent_count; i > 0; i--)
        if (((sent[i - 1].id >> 6) & 1023) == api)
            return &sent[i - 1];
    return NULL;
}
int main(int argc, char **argv) {
    CHECK(argc == 2);
    scenario = argv[1];
    if (is("reserved_channel")) {
        config.invert_mask = 9; /* Old stored bit3 is sanitized. */
        command(20, SC_API_CONFIG, 8, 2, 0); /* Invalid fourth-channel mask cannot turn rails off. */
    } else if (is("watchdog_reset")) {
        host_rcc_state.CSR = RCC_CSR_IWDGRSTF;
        command(100, SC_API_CLEAR_FAULT, 3, 0, 0);
    } else if (is("fault_disable_recovery")) {
        command(35, SC_API_CLEAR_FAULT, 1, 0, 0);
        command(120, SC_API_CLEAR_FAULT, 1, 0, 0);
        pending[pending_count++] = (frame){.at = 140, .id = 0, .len = 0};
        command(160, SC_API_CONFIG, 1, 2, 3);
        command(200, SC_API_CLEAR_FAULT, 3, 0, 0);
        command(240, SC_API_CLEAR_FAULT, 3, 0, 0);
    } else if (is("bad_commands")) {
        command(20, SC_API_CONFIG, 0, 2, 0);
        pending[pending_count - 1].data[0] = 0;
        command(21, SC_API_CONFIG, 0, 2, 0);
        pending[pending_count - 1].len = 7;
        command(22, SC_API_CONFIG, 0, 0, 0);
        command(23, SC_API_CONFIG, 0, 2, 4);
        command(24, SC_API_CONFIG, 0, 2, 0);
        pending[pending_count - 1].id = sc_can_id(18, SC_API_CONFIG);
        command(25, SC_API_CONFIG, 0, 2, 0);
        pending[pending_count - 1].data[7] = 1;
        command(26, SC_API_CLEAR_FAULT, 3, 1, 0);
        command(50, SC_API_CONFIG, 2, 3, 1);
    } else if (is("battery_short") || is("battery_voltage_loss")) {
        command(35, SC_API_CLEAR_FAULT, 2, 0, 0);
        command(120, SC_API_CLEAR_FAULT, 2, 0, 0);
    } else if (is("uart_set"))
        serial_in = "SET 23 5 7 1\r";
    else if (is("uart_overflow"))
        serial_in = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                    "AA\rINFO\r";
    else if (is("unconfigured"))
        serial_in = "INFO\r";
    int reason = setjmp(done);
    if (!reason) {
        (void)firmware_main();
        CHECK(false);
    }
    if (is("uart_set")) {
        CHECK(reason == 2 && resets == 1 && stores == 1);
        CHECK(saved.device_id == 23 && saved.invert_mask == 5 && saved.debounce_ms == 7 &&
              saved.rail_mask == 1);
        CHECK(strstr(serial_out, "OK: saved; resetting") != NULL);
    } else if (is("scheduler_stall")) {
        CHECK(reason == 3 && stops == 1 && physical_rails == 0 && standby && feeds == 49);
    } else {
        CHECK(reason == 1 && feeds == 400 && resets == 0 && stores == 0);
        if (is("unconfigured") || is("clock_failure")) {
            CHECK(can_inits == 0 && sent_count == 0 && standby);
            for (unsigned t = 0; t <= 400; t++)
                CHECK(output_at[t] == 0);
            CHECK(red_at[200]);
        } else if (is("can_init_failure")) {
            CHECK(can_inits == 1 && sent_count == 0 && standby);
            CHECK(red_at[200]);
        } else {
            CHECK(can_inits == 1 && !standby && sent_count > 40);
            const frame *s = last_api(SC_API_STATUS);
            CHECK(s && s->data[0] == 1);
            for (unsigned i=0;i<sent_count;i++) {
                unsigned api=(sent[i].id>>6)&1023u;
                if(api==SC_API_STATUS) CHECK((sent[i].data[2]&8u)==0 && (sent[i].data[3]&8u)==0);
                if(api==SC_API_COUNTS34) CHECK((sent[i].data[4]|sent[i].data[5]|sent[i].data[6]|sent[i].data[7])==0);
            }
            CHECK(s->data[3] == 0); /* Electrical raw; independent of invert mask. */
            if (is("watchdog_reset")) {
                for (unsigned t = 0; t <= 100; t++)
                    CHECK(output_at[t] == 0);
                CHECK(output_at[101] == 3 && s->data[7] == 4);
            } else if (is("fault_disable_recovery")) {
                CHECK(output_at[19] == 3 && output_at[20] == 2 && output_at[119] == 2);
                CHECK(output_at[121] == 3 && output_at[139] == 3 && output_at[140] == 0);
                CHECK(output_at[239] == 0 && output_at[240] == 0 && output_at[241] == 3);
                CHECK(s->data[4] == 3 && s->data[5] == 0);
            } else if (is("bad_commands")) {
                for (unsigned t = 1; t <= 50; t++)
                    CHECK(output_at[t] == 3);
                CHECK(output_at[51] == 1 && s->data[2] == 2 && s->data[4] == 1);
            } else if (is("adc_failure")) {
                CHECK((s->data[6] & 4) == 0 && red_at[200]);
                CHECK(output_at[5] == 3 && output_at[6] == 0 && s->data[5] == 3);
            } else if (is("adc_runtime_failure")) {
                CHECK(output_at[19] == 3 && output_at[20] == 0);
                CHECK(s->data[4] == 0 && s->data[5] == 3 && !(s->data[6] & 4));
            } else if (is("battery_short") || is("battery_voltage_loss")) {
                CHECK(output_at[19] == 3 && output_at[20] == 1 && output_at[119] == 1);
                CHECK(output_at[120] == 1 && output_at[121] == 3);
                CHECK(s->data[4] == 3 && s->data[5] == 0);
            } else if (is("startup_timeout")) {
                CHECK(output_at[5] == 3 && output_at[6] == 1 && s->data[5] == 2);
            } else {
                CHECK(s->data[2] == 1 && s->data[4] == 3 && s->data[5] == 0 && s->data[6] == 7);
                const frame *c = last_api(SC_API_COUNTS12);
                CHECK(c && c->data[0] == 1 && c->data[4] == 0);
                if (is("can_busy")) {
                    const frame *d = last_api(SC_API_DIAGNOSTIC);
                    CHECK(d && (d->data[4] | ((unsigned)d->data[5] << 8)) > 0);
                }
                if (is("uart_overflow"))
                    CHECK(strstr(serial_out, "ERR: serial line discarded") &&
                          strstr(serial_out, "configured=1"));
            }
        }
    }
    printf("PASS application %-24s %u assertions\n", scenario, checks);
}
