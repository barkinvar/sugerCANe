#ifndef BOARD_H
#define BOARD_H
/* Host boundary model for testing the real main.c scheduler and protocol.
 * This is not an STM32 peripheral emulator. Register code is built separately. */
#include "sensor_core.h"
#include <stdint.h>
typedef struct {
    volatile uint32_t IDR;
} host_gpio;
typedef struct {
    volatile uint32_t CSR;
} host_rcc;
typedef struct {
    volatile uint32_t ESR;
} host_can;
extern host_gpio host_gpioa;
extern host_rcc host_rcc_state;
extern host_can host_can_state;
#define GPIOA (&host_gpioa)
#define RCC (&host_rcc_state)
#define CAN (&host_can_state)
#define CAN_ESR_BOFF (1u<<2)
#define CAN_ESR_EPVF (1u<<1)
#define RCC_CSR_PORRSTF (1u << 27)
#define RCC_CSR_PINRSTF (1u << 26)
#define RCC_CSR_IWDGRSTF (1u << 29)
#define RCC_CSR_SFTRSTF (1u << 28)
#define RCC_CSR_RMVF (1u << 24)
extern volatile uint32_t board_millis;
extern uint32_t SystemCoreClock;
int SysTick_Config(uint32_t ticks);
_Noreturn void NVIC_SystemReset(void);
void host_wait(void);
#define __WFI() host_wait()
bool board_clock_init(void);
void board_voltage_guard_init(void);
void board_gpio_init(void);
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
void board_status_led(bool on);
bool board_config_store(sc_config_record *record);
const sc_config_record *board_config_load(void);
void board_safe_off(void);
#endif
