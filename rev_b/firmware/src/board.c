#include "board.h"
#include <string.h>
uint32_t SystemCoreClock = 8000000u;
volatile uint32_t board_millis;
#define FLASH_A ((const sc_config_record *)0x08007800u)
#define FLASH_B ((const sc_config_record *)0x08007c00u)
#define VREFINT_CAL_ADDR ((const uint16_t *)0x1ffff7bau)
void _init(void) {}
void _fini(void) {}
void SystemInit(void) { /* Reset starts on the 8MHz HSI. GPIO defaults keep rails off. */ }
void SysTick_Handler(void) {
    board_millis++;
}
static bool wait_bits(volatile uint32_t *reg, uint32_t mask, uint32_t value, uint32_t loops) {
    while (loops--)
        if ((*reg & mask) == value)
            return true;
    return false;
}
static void gpio_mode(GPIO_TypeDef *port, unsigned pin, unsigned mode) {
    port->MODER = (port->MODER & ~(3u << (pin * 2))) | (mode << (pin * 2));
}
static void gpio_af(GPIO_TypeDef *port, unsigned pin, unsigned af) {
    unsigned n = pin / 8, shift = (pin % 8) * 4;
    port->AFR[n] = (port->AFR[n] & ~(15u << shift)) | (af << shift);
    gpio_mode(port, pin, 2);
}
void board_gpio_init(void) {
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN | RCC_AHBENR_GPIOBEN | RCC_AHBENR_GPIOFEN;
    (void)RCC->AHBENR;
    GPIOA->BSRR = (1u << 8);
    GPIOB->BSRR = (3u << 16); /* STB high; enables low before output mode. */
    for (unsigned i = 0; i < 3; i++)
        gpio_mode(GPIOA, i, 0);
    gpio_mode(GPIOA, 3, 3); /* Rev B unused fourth input: analog, no floating digital input. */
    gpio_mode(GPIOA, 4, 3);
    gpio_mode(GPIOA, 5, 3);
    for (unsigned i = 6; i <= 8; i++)
        gpio_mode(GPIOA, i, 1);
    gpio_mode(GPIOA, 15, 1);
    for (unsigned i = 0; i <= 1; i++)
        gpio_mode(GPIOB, i, 1);
    gpio_mode(GPIOB, 3, 1);
    gpio_mode(GPIOB, 4, 0);
    gpio_mode(GPIOB, 5, 0);
    gpio_mode(GPIOB, 6, 1);
    gpio_mode(GPIOB, 7, 3); /* Rev B has three input LEDs. */
    /* SWD PA13/PA14 deliberately keep their reset alternate function. */
}
void board_voltage_guard_init(void) {
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    (void)RCC->APB1ENR;
    /* Level7: nominal falling2.78V, min2.66V (STM32F042 DS Table24).
       A low logic rail must turn sensor power off before unreliable operation. */
    PWR->CR = (PWR->CR & ~PWR_CR_PLS) | PWR_CR_PLS_LEV7 | PWR_CR_PVDE;
    for (unsigned i = 0; i < 1000; i++)
        __NOP();
    EXTI->RTSR |= EXTI_RTSR_TR16;
    EXTI->FTSR &= ~EXTI_FTSR_TR16;
    EXTI->PR = EXTI_PR_PR16;
    EXTI->IMR |= EXTI_IMR_MR16;
    NVIC_SetPriority(PVD_VDDIO2_IRQn, 0);
    NVIC_EnableIRQ(PVD_VDDIO2_IRQn);
    if (PWR->CSR & PWR_CSR_PVDO) {
        board_safe_off();
        for (;;) {
        } /* Independent watchdog reset; rails latch off after restart. */
    }
}
void PVD_VDDIO2_IRQHandler(void) {
    EXTI->PR = EXTI_PR_PR16;
    if (PWR->CSR & PWR_CSR_PVDO) {
        board_safe_off();
        for (;;) {
        }
    }
}
bool board_clock_init(void) {
    RCC->CR |= RCC_CR_HSEON;
    if (!wait_bits(&RCC->CR, RCC_CR_HSERDY, RCC_CR_HSERDY, 200000u))
        return false;
    FLASH->ACR = FLASH_ACR_PRFTBE | FLASH_ACR_LATENCY;
    RCC->CFGR2 = 0; /* HSE predivider /1 */
    RCC->CFGR = RCC_CFGR_PLLSRC_HSE_PREDIV | RCC_CFGR_PLLMUL6;
    RCC->CR |= RCC_CR_PLLON;
    if (!wait_bits(&RCC->CR, RCC_CR_PLLRDY, RCC_CR_PLLRDY, 200000u))
        return false;
    RCC->CFGR |= RCC_CFGR_SW_PLL;
    if (!wait_bits(&RCC->CFGR, RCC_CFGR_SWS, RCC_CFGR_SWS_PLL, 200000u))
        return false;
    SystemCoreClock = 48000000u;
    RCC->CR |= RCC_CR_CSSON;
    return true;
}
void board_set_rails(uint8_t mask) {
    /* Protocol bit0 = 5V / PB1; bit1 = battery / PB0. */
    uint32_t bits = ((mask & 1u) << 1) | ((mask & 2u) >> 1);
    GPIOB->BSRR = bits | ((3u & ~bits) << 16);
}
uint8_t board_faults(void) {
    uint32_t v = ~GPIOB->IDR;
    return (uint8_t)(((v >> 5) & 1u) | (((v >> 4) & 1u) << 1));
}
void board_can_standby(bool value) {
    GPIOA->BSRR = value ? (1u << 8) : (1u << (8 + 16));
}
void board_safe_off(void) {
    board_set_rails(0);
    board_can_standby(true);
}
void NMI_Handler(void) {
    board_safe_off();
    for (;;) { /* Clock security failure: IWDG resets. */
    }
}
void HardFault_Handler(void) {
    board_safe_off();
    for (;;) {
    }
}
void board_leds(uint8_t inputs, bool green, bool red) {
    uint32_t a = ((inputs & 1u) << 6) | ((inputs & 2u) << 6) | (red ? (1u << 15) : 0);
    uint32_t am = (3u << 6) | (1u << 15);
    GPIOA->BSRR = a | ((am & ~a) << 16);
    uint32_t z = ((inputs & 4u) << 4) | (green ? (1u << 3) : 0);
    uint32_t zm = (1u << 6) | (1u << 3);
    GPIOB->BSRR = z | ((zm & ~z) << 16);
}
static uint8_t uart_tx[512], uart_rx[128];
static volatile uint16_t tx_head, tx_tail, rx_head, rx_tail;
static volatile bool rx_error;
void board_uart_init(void) {
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;
    gpio_af(GPIOA, 9, 1);
    gpio_af(GPIOA, 10, 1);
    USART1->BRR = (SystemCoreClock + 57600u) / 115200u;
    USART1->CR3 = USART_CR3_EIE;
    USART1->CR1 = USART_CR1_UE | USART_CR1_TE | USART_CR1_RE | USART_CR1_RXNEIE;
    NVIC_SetPriority(USART1_IRQn, 2);
    NVIC_EnableIRQ(USART1_IRQn);
}
void USART1_IRQHandler(void) {
    uint32_t isr = USART1->ISR;
    if (isr & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE)) {
        USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
        rx_error = true;
    }
    if (isr & USART_ISR_RXNE) {
        uint8_t c = (uint8_t)USART1->RDR;
        uint16_t next = (uint16_t)((rx_head + 1u) & 127u);
        if (next == rx_tail)
            rx_error = true;
        else {
            uart_rx[rx_head] = c;
            __DMB();
            rx_head = next;
        }
    }
    if ((isr & USART_ISR_TXE) && (USART1->CR1 & USART_CR1_TXEIE)) {
        if (tx_head == tx_tail)
            USART1->CR1 &= ~USART_CR1_TXEIE;
        else {
            USART1->TDR = uart_tx[tx_tail];
            tx_tail = (uint16_t)((tx_tail + 1u) & 511u);
        }
    }
}
void board_uart_write(const char *s) {
    while (*s) {
        uint16_t next = (uint16_t)((tx_head + 1u) & 511u);
        if (next == tx_tail)
            break; /* Bound diagnostic output under command flooding. */
        uart_tx[tx_head] = (uint8_t)*s++;
        __DMB();
        tx_head = next;
    }
    USART1->CR1 |= USART_CR1_TXEIE;
}
void board_uart_flush(void) {
    uint32_t start = board_millis;
    while ((tx_head != tx_tail || !(USART1->ISR & USART_ISR_TC)) &&
           (uint32_t)(board_millis - start) < 100u)
        __WFI();
}
int board_uart_get(void) {
    /* Read-and-clear cannot lose an ISR error that arrives between the two operations. */
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    bool error = rx_error;
    rx_error = false;
    __set_PRIMASK(primask);
    if (error)
        return -2;
    if (rx_head == rx_tail)
        return -1;
    uint8_t c = uart_rx[rx_tail];
    rx_tail = (uint16_t)((rx_tail + 1u) & 127u);
    return c;
}
void board_watchdog_start(void) {
    IWDG->KR = 0xcccc;
    IWDG->KR = 0x5555;
    IWDG->PR = 4; /* LSI /64; ~1s nominal, 0.8..1.33s for 30..50kHz. */
    IWDG->RLR = 624;
    wait_bits(&IWDG->SR, 7, 0, 100000u);
    IWDG->KR = 0xaaaa;
}
void board_watchdog_feed(void) {
    IWDG->KR = 0xaaaa;
}
bool board_can_init(uint8_t id) {
    RCC->APB1ENR |= RCC_APB1ENR_CANEN;
    gpio_af(GPIOA, 11, 4);
    gpio_af(GPIOA, 12, 4);
    CAN->MCR = CAN_MCR_INRQ | CAN_MCR_ABOM | CAN_MCR_NART;
    if (!wait_bits(&CAN->MSR, CAN_MSR_INAK, CAN_MSR_INAK, 1000000u))
        return false;
    CAN->BTR = (2u << CAN_BTR_BRP_Pos) | (12u << CAN_BTR_TS1_Pos) | (1u << CAN_BTR_TS2_Pos);
    CAN->FMR |= CAN_FMR_FINIT;
    CAN->FA1R = 0;
    CAN->FM1R = 0;
    CAN->FS1R = 3;
    CAN->FFA1R = 2; /* Broadcast Disable has its own FIFO, ahead of normal commands. */
    CAN->sFilterRegister[0].FR1 = (sc_can_id(id, 0) << 3) | CAN_RI0R_IDE;
    CAN->sFilterRegister[0].FR2 = (0x1fff003fu << 3) | CAN_RI0R_IDE | CAN_RI0R_RTR;
    CAN->sFilterRegister[1].FR1 = CAN_RI0R_IDE; /* Extended data frame ID0. */
    CAN->sFilterRegister[1].FR2 = 0xfffffffeu;  /* Exact ID, IDE and RTR. */
    CAN->FA1R = 3;
    CAN->FMR &= ~CAN_FMR_FINIT;
    CAN->MCR &= ~CAN_MCR_INRQ;
    /* RXD is recessive in initial transceiver standby. Bound initialization. */
    return wait_bits(&CAN->MSR, CAN_MSR_INAK, 0, 100000u);
}
bool board_can_send(uint32_t id, const uint8_t data[8]) {
    if (CAN->ESR & CAN_ESR_BOFF)
        return false;
    uint32_t tsr = CAN->TSR;
    for (unsigned i = 0; i < 3; i++)
        if (tsr & (CAN_TSR_TME0 << i)) {
            uint32_t lo, hi;
            memcpy(&lo, data, 4);
            memcpy(&hi, data + 4, 4);
            CAN->sTxMailBox[i].TDTR = 8;
            CAN->sTxMailBox[i].TDLR = lo;
            CAN->sTxMailBox[i].TDHR = hi;
            CAN->sTxMailBox[i].TIR = (id << 3) | CAN_TI0R_IDE | CAN_TI0R_TXRQ;
            return true;
        }
    return false;
}
bool board_can_receive(uint32_t *id, uint8_t data[8], uint8_t *len) {
    unsigned fifo;
    if (CAN->RF1R & CAN_RF1R_FMP1)
        fifo = 1;
    else if (CAN->RF0R & CAN_RF0R_FMP0)
        fifo = 0;
    else
        return false;
    uint32_t rir = CAN->sFIFOMailBox[fifo].RIR;
    uint32_t lo = CAN->sFIFOMailBox[fifo].RDLR, hi = CAN->sFIFOMailBox[fifo].RDHR;
    *len = (uint8_t)(CAN->sFIFOMailBox[fifo].RDTR & 15);
    *id = rir >> 3;
    memcpy(data, &lo, 4);
    memcpy(data + 4, &hi, 4);
    if (fifo)
        CAN->RF1R = CAN_RF1R_RFOM1;
    else
        CAN->RF0R = CAN_RF0R_RFOM0;
    if (!(rir & CAN_RI0R_IDE) || (rir & CAN_RI0R_RTR) || *len > 8) {
        *len = 0;
        *id = UINT32_MAX;
    }
    return true;
}
bool board_adc_init(void) {
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    RCC->CR2 |= RCC_CR2_HSI14ON;
    if (!wait_bits(&RCC->CR2, RCC_CR2_HSI14RDY, RCC_CR2_HSI14RDY, 100000u))
        return false;
    ADC1->CR = ADC_CR_ADCAL;
    if (!wait_bits(&ADC1->CR, ADC_CR_ADCAL, 0, 100000u))
        return false;
    /* ES0243 2.5.3: ADEN may be reset during the four ADC clocks after ADCAL clears.
       64 core NOPs exceed four 14MHz ADC clocks even with the CPU at 48MHz. */
    for (unsigned i = 0; i < 64; i++)
        __NOP();
    ADC1->SMPR = ADC_SMPR_SMP;
    ADC->CCR |= ADC_CCR_VREFEN;
    ADC1->ISR = ADC_ISR_ADRDY;
    ADC1->CR = ADC_CR_ADEN;
    return wait_bits(&ADC1->ISR, ADC_ISR_ADRDY, ADC_ISR_ADRDY, 100000u);
}
static bool adc_read(unsigned channel, uint16_t *out) {
    ADC1->CHSELR = 1u << channel;
    ADC1->ISR = ADC_ISR_EOC | ADC_ISR_EOS | ADC_ISR_OVR;
    ADC1->CR |= ADC_CR_ADSTART;
    if (!wait_bits(&ADC1->ISR, ADC_ISR_EOC, ADC_ISR_EOC, 100000u))
        return false;
    *out = (uint16_t)ADC1->DR;
    return true;
}
bool board_adc_millivolts(uint16_t *battery, uint16_t *sensor5) {
    uint16_t ref, a, c;
    uint16_t cal = *VREFINT_CAL_ADDR;
    if (!adc_read(17, &ref) || !adc_read(4, &a) || !adc_read(5, &c) || ref == 0 || cal == 0 ||
        cal == 0xffff)
        return false;
    /* Factory VREFINT calibration is measured at VDDA=3.3V. Resistors remain 1%. */
    uint32_t vdda = 3300u * cal / ref;
    if (vdda < 2500 || vdda > 3600)
        return false;
    *battery = (uint16_t)((uint32_t)a * vdda * 11u / 4095u);
    *sensor5 = (uint16_t)((uint32_t)c * vdda * 2u / 4095u);
    return true;
}
const sc_config_record *board_config_load(void) {
    int n = sc_config_newest(FLASH_A, FLASH_B);
    return n < 0 ? 0 : (n == 0 ? FLASH_A : FLASH_B);
}
static bool flash_ready(void) {
    if (!wait_bits(&FLASH->SR, FLASH_SR_BSY, 0, 4000000u))
        return false;
    return !(FLASH->SR & (FLASH_SR_PGERR | FLASH_SR_WRPRTERR));
}
bool board_config_store(sc_config_record *record) {
    const sc_config_record *current = board_config_load();
    uint32_t address = current == FLASH_A ? (uint32_t)FLASH_B : (uint32_t)FLASH_A;
    record->magic = SC_CONFIG_MAGIC;
    record->version = 1;
    record->sequence = current ? current->sequence + 1u : 1u;
    record->reserved0 = 0;
    record->reserved1 = record->reserved2 = 0;
    record->commit = SC_CONFIG_COMMIT;
    record->crc = sc_crc32(record, 24);
    if (!sc_config_valid(record))
        return false;
    board_safe_off();
    __disable_irq();
    FLASH->KEYR = 0x45670123u;
    FLASH->KEYR = 0xcdef89abu;
    FLASH->SR = FLASH_SR_EOP | FLASH_SR_PGERR | FLASH_SR_WRPRTERR;
    bool ok = flash_ready();
    if (ok) {
        FLASH->CR = FLASH_CR_PER;
        FLASH->AR = address;
        FLASH->CR |= FLASH_CR_STRT;
        ok = flash_ready();
        FLASH->CR = 0;
    }
    for (unsigned i = 0; ok && i < 16; i++) {
        uint16_t word;
        memcpy(&word, (const uint8_t *)record + 2 * i, sizeof(word));
        FLASH->CR = FLASH_CR_PG;
        *(volatile uint16_t *)(address + 2 * i) = word;
        ok = flash_ready();
        FLASH->CR = 0;
    }
    FLASH->CR = FLASH_CR_LOCK;
    __enable_irq();
    return ok && sc_config_valid((const sc_config_record *)address);
}
