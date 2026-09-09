#ifndef BOARD_H
#define BOARD_H
#include "sensor_core.h"
#include "status.h"
#include "stm32f0xx.h"
extern volatile uint32_t board_millis;
extern uint32_t SystemCoreClock;
bool board_clock_init(void);
void board_voltage_guard_init(void);
void board_gpio_init(void);
void board_bias(uint8_t up,uint8_t down);
void board_uart_init(void);
void board_uart_write(const char *s);
int board_uart_get(void);
void board_uart_flush(void);
void board_watchdog_start(void);
void board_watchdog_feed(void);
bool board_can_init(uint8_t id);
bool board_can_send(uint32_t id, const uint8_t data[8]);
bool board_can_receive(uint32_t *id, uint8_t data[8], uint8_t *len);
void board_can_standby(bool value);
void board_can_abort(void);
void board_status_init(void);
void board_status_stop(void);
void board_status_led(uint32_t rgb);
bool board_can_link_ok(uint32_t now);
bool board_config_store(sc_config_record *record);
const sc_config_record *board_config_load(void);
void board_safe_off(void);
void board_power_set(uint8_t enabled);
bool board_adc_init(void);
bool board_rail_read(uint16_t *mv12,uint16_t *mv5);
#endif
