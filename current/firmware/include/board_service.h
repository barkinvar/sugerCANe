#ifndef BOARD_SERVICE_H
#define BOARD_SERVICE_H
#include "service.h"
void board_service_init(sc_service *,bool boot);
void board_boot_request(bool stay);
bool board_boot_stay(void);
void board_boot_healthy(void);
void board_run_application(void) __attribute__((noreturn));
#endif
