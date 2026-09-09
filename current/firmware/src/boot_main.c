#include "board.h"
#include "board_service.h"
static sc_service service;
int main(void) {
    board_gpio_init();bool stay=board_boot_stay();board_watchdog_start();board_voltage_guard_init();
    bool clock_ok=board_clock_init();SysTick_Config(SystemCoreClock/1000u);board_status_init();
    board_service_init(&service,true);
    bool valid=sc_image_valid(&service.io);
    const sc_config_record *cfg=board_config_load();
    bool can_ok=clock_ok && board_can_init(cfg?cfg->device_id:0);
    if(can_ok)board_can_standby(false);
    uint32_t last=0;
    for(;;) {
        uint32_t now=board_millis;
        if(now!=last){last=now;
            if(can_ok)for(unsigned n=0;n<3;n++) {
                uint32_t id;uint8_t data[8],len;
                if(!board_can_receive(&id,data,&len))break;
                if(id==0){sc_service_disable(&service);board_can_abort();stay=true;break;}
                if(id==SC_SERVICE_RX && len==8){
                    sc_service_receive(&service,data,now);
                    if(service.updating)stay=true;
                }
            }
            sc_service_tick(&service,now);
            sc_led_state led= !clock_ok ? SC_LED_POWER_FAULT :
                service.blink_until && (uint32_t)(service.blink_until-now)<0x80000000u ? SC_LED_IDENTIFY : SC_LED_BOOT;
            board_status_led(sc_status_color(led,now));
            /* Recheck after maintenance, including a partially failed manifest erase. */
            if(valid && !stay && now>=500 && !sc_service_active(&service)) {
                if(sc_image_valid(&service.io))board_run_application();
                stay=true;
            }
            board_watchdog_feed();
        }
        __WFI();
    }
}
