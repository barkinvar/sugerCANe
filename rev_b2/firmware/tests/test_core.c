#include "sensor_core.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x)                                                                                   \
    do {                                                                                           \
        assert(x);                                                                                 \
        checks++;                                                                                  \
    } while (0)
static sc_config_record record(uint32_t seq) {
    sc_config_record r = {.magic = SC_CONFIG_MAGIC,
                          .sequence = seq,
                          .version = 1,
                          .device_id = 17,
                          .invert_mask = 5,
                          .debounce_ms = 2,
                          .rail_mask = 3,
                          .commit = SC_CONFIG_COMMIT};
    r.crc = sc_crc32(&r, 24);
    return r;
}
static void test_flash_records(void) {
    CHECK(sc_crc32("123456789", 9) == 0xcbf43926u);
    sc_config_record a = record(1), b = record(2), c;
    CHECK(sc_config_valid(&a));
    CHECK(sc_config_newest(&a, &b) == 1);
    /* Simulate power loss after each halfword of a fresh record is programmed. */
    for (unsigned n = 0; n < 16; n++) {
        memset(&c, 255, sizeof(c));
        memcpy(&c, &b, n * 2);
        CHECK(!sc_config_valid(&c));
        CHECK(sc_config_newest(&a, &c) == 0);
    }
    /* Detect every single-bit corruption in the persisted record. */
    for (unsigned bit = 0; bit < 256; bit++) {
        c = b;
        ((uint8_t *)&c)[bit / 8] ^= (uint8_t)(1u << (bit % 8));
        CHECK(!sc_config_valid(&c));
    }
    a = record(0xffffffffu);
    b = record(0);
    CHECK(sc_config_newest(&a, &b) == 1);
    memset(&a, 255, sizeof(a));
    memset(&b, 255, sizeof(b));
    CHECK(sc_config_newest(&a, &b) == -1);
    for (unsigned id = 0; id < 256; id++) {
        a = record(1);
        a.device_id = (uint8_t)id;
        a.crc = sc_crc32(&a, 24);
        CHECK(sc_config_valid(&a) == (id < 64));
    }
}
static void test_inputs(void) {
    sc_inputs s;
    sc_inputs_init(&s, 15, 0, 2, 0);
    CHECK(s.stable == 15);
    CHECK(s.rising[0] == 0); /* Boot is not an edge. */
    sc_inputs_update(&s, 0, 1);
    sc_inputs_update(&s, 0, 2);
    CHECK(s.stable == 15);
    sc_inputs_update(&s, 0, 3);
    CHECK(s.stable == 0);
    sc_inputs_update(&s, 1, 4);
    sc_inputs_update(&s, 0, 5);
    sc_inputs_update(&s, 0, 20);
    CHECK(s.stable == 0);
    CHECK(s.rising[0] == 0);
    sc_inputs_update(&s, 1, 21);
    sc_inputs_update(&s, 1, 23);
    CHECK(s.stable == 1);
    CHECK(s.rising[0] == 1);
    sc_inputs_init(&s, 0, 0, 2, 0xfffffffeu);
    sc_inputs_update(&s, 1, 0xffffffffu);
    sc_inputs_update(&s, 1, 0);
    CHECK(s.stable == 0);
    sc_inputs_update(&s, 1, 1);
    CHECK(s.stable == 1);
    sc_inputs_init(&s, 0, 15, 2, 0);
    CHECK(s.stable == 15);
    CHECK(s.rising[0] == 0);
    /* Deterministic randomized reference: require debounce+1 consecutive sampled
       values before accepting a transition. Tests all channels, masks and timing. */
    uint32_t rng = 0x129abcefu;
    for (unsigned invert = 0; invert < 16; invert++)
        for (unsigned debounce = 1; debounce <= 10; debounce++) {
            sc_inputs_init(&s, 0, (uint8_t)invert, (uint16_t)debounce, 0);
            uint8_t prev = (uint8_t)invert, stable = prev;
            unsigned runs[4] = {1, 1, 1, 1};
            uint32_t count[4] = {0};
            for (uint32_t t = 1; t < 2000; t++) {
                rng = rng * 1664525u + 1013904223u;
                uint8_t raw = (uint8_t)((rng >> 28) & 15), logical = raw ^ (uint8_t)invert;
                for (unsigned ch = 0; ch < 4; ch++) {
                    uint8_t bit = (uint8_t)(1u << ch);
                    runs[ch] = ((logical ^ prev) & bit) ? 1 : runs[ch] + 1;
                    if (runs[ch] >= debounce + 1 && ((logical ^ stable) & bit)) {
                        stable ^= bit;
                        if (stable & bit)
                            count[ch]++;
                    }
                }
                prev = logical;
                sc_inputs_update(&s, raw, t);
                CHECK(s.stable == stable);
                for (unsigned ch = 0; ch < 4; ch++)
                    CHECK(s.rising[ch] == count[ch]);
            }
        }
}
static void test_rails(void) {
    /* Exhaust every ADC code-in-millivolts across the exact delivery threshold.
       An asserted battery FAULT with healthy voltage is the legitimate low-load
       condition from TPS1H200A, not an instruction to disconnect the sensor. */
    for (unsigned mv = 0; mv <= 65535; mv++) {
        CHECK(sc_power_faults(0, true, (uint16_t)mv, 5000) == (mv < 4500 ? 2 : 0));
        CHECK(sc_power_faults(2, true, (uint16_t)mv, 5000) == (mv < 4500 ? 2 : 0));
        CHECK(sc_power_faults(0, true, 12000, (uint16_t)mv) == (mv < 4500 ? 1 : 0));
        CHECK(sc_power_faults(1, true, 12000, (uint16_t)mv) == 1);
        CHECK(sc_power_faults(0, false, (uint16_t)mv, 5000) == 3);
    }
    for (uint8_t mask = 0; mask < 4; mask++) {
        sc_rails emergency;
        sc_rails_init(&emergency, mask, false, 0);
        sc_rails_update(&emergency, 0, 1);
        sc_rails_emergency_off(&emergency, 20);
        CHECK(emergency.enabled == 0 && emergency.requested == 0 && emergency.latched == 3);
        emergency.requested = mask;
        sc_rails_update(&emergency, 0, 100);
        CHECK(emergency.enabled == 0);
        CHECK(!sc_rails_clear(&emergency, 3, 119));
        CHECK(sc_rails_clear(&emergency, 3, 120));
        sc_rails_update(&emergency, 0, 121);
        CHECK(emergency.enabled == mask);
    }

    for (uint8_t requested = 0; requested < 4; requested++) {
        sc_rails boot;
        sc_rails_init(&boot, requested, false, 42);
        sc_rails_update(&boot, 0, 43);
        CHECK(boot.enabled == requested);
        sc_rails_init(&boot, requested, true, 42);
        for (uint32_t t = 43; t < 200; t++) {
            sc_rails_update(&boot, 0, t);
            CHECK(boot.enabled == 0);
            CHECK(boot.latched == 3);
        }
        CHECK(!sc_rails_clear(&boot, 3, 141));
        CHECK(sc_rails_clear(&boot, 3, 142));
        sc_rails_update(&boot, 0, 143);
        CHECK(boot.enabled == requested);
    }
    sc_rails s = {0};
    sc_rails_update(&s, 3, 0);
    CHECK(s.enabled == 0);
    CHECK(s.latched == 0);
    s.requested = 3;
    sc_rails_update(&s, 0, 1);
    CHECK(s.enabled == 3);
    sc_rails_update(&s, 1, 5);
    CHECK(s.enabled == 3);
    sc_rails_update(&s, 1, 6);
    CHECK(s.enabled == 2);
    CHECK(s.latched == 1);
    for (uint32_t t = 7; t < 100; t++) {
        sc_rails_update(&s, 0, t);
        CHECK(s.enabled == 2);
    } /* No automatic retry. */
    CHECK(!sc_rails_clear(&s, 1, 105));
    CHECK(sc_rails_clear(&s, 1, 106));
    sc_rails_update(&s, 0, 106);
    CHECK(s.enabled == 3);
    sc_rails_update(&s, 1, 111);
    CHECK(s.enabled == 2);
    CHECK(s.latched == 1);
    CHECK(!sc_rails_clear(&s, 0, 1000));
    CHECK(!sc_rails_clear(&s, 4, 1000));
    CHECK(!sc_rails_clear(&s, 2, 1000));
    s.requested = 0;
    sc_rails_update(&s, 0, 112);
    CHECK(s.enabled == 0);
    s = (sc_rails){.latched = 1, .disabled_at = {0xfffffff0u, 0}};
    CHECK(!sc_rails_clear(&s, 1, 0x20));
    CHECK(sc_rails_clear(&s, 1, 0x60));
}
static void test_can_ids(void) {
    CHECK(sc_can_id(17, SC_API_STATUS) == 0x0a084011u);
    for (unsigned d = 0; d < 64; d++)
        for (unsigned api = 0; api < 1024; api++) {
            uint32_t id = sc_can_id((uint8_t)d, (uint16_t)api);
            CHECK(id < 0x20000000u);
            CHECK(sc_can_is_ours(id, (uint8_t)d));
            CHECK(!sc_can_is_ours(id, (uint8_t)((d + 1) % 64)));
            CHECK(!sc_can_is_ours(id ^ (1u << 16), (uint8_t)d));
        }
    uint8_t b[4];
    sc_put_u32(b, 0x89abcdefu);
    CHECK(b[0] == 0xef && b[1] == 0xcd && b[2] == 0xab && b[3] == 0x89);
}
int main(void) {
    test_flash_records();
    test_inputs();
    test_rails();
    test_can_ids();
    printf("PASS: %u core assertions (including power-loss, debounce fuzz, rollover, fault latch, "
           "CAN filters)\n",
           checks);
    return 0;
}
