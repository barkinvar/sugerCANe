#ifndef SC_SERVICE_H
#define SC_SERVICE_H
#include "sensor_core.h"
#define SC_APP_BASE 0x08002000u
#define SC_APP_SIZE (21u*1024u)
#define SC_MANIFEST 0x08007400u
#define SC_SERVICE_RX ((10u<<24)|(8u<<16)|(0x300u<<6))
#define SC_SERVICE_TX ((10u<<24)|(8u<<16)|(0x301u<<6))
#define SC_SERVICE_MAGIC 0x314d4353u
#define SC_IMAGE_TAG 0x53433138u
#define SC_IMAGE_MAGIC 0x49324353u
#define SC_IMAGE_COMMIT 0xc035a19eu
#define SC_LEASE_MS 5000u
enum { SC_OPEN=1, SC_PREFIX0, SC_PREFIX1, SC_PREFIX2, SC_PROBE, SC_CLOSE,
       SC_INFO=0x10, SC_BLINK, SC_SAVE, SC_BOOT, SC_RUN, SC_RATE, SC_INPUTS, SC_POWER,
       SC_SIZE=0x20, SC_CRC, SC_BEGIN, SC_OFFSET, SC_DATA, SC_FINISH };
enum { SC_OK=0, SC_BAD_ARGUMENT=1, SC_BAD_STATE, SC_FLASH_ERROR,
       SC_BAD_IMAGE, SC_NOT_PROTECTED };
/* Callbacks are the only hardware boundary; the same engine runs in host tests. */
typedef struct {
    void *ctx;
    bool (*read)(void *,uint32_t,void *,uint32_t);
    bool (*erase)(void *,uint32_t);
    bool (*write)(void *,uint32_t,const void *,uint32_t);
    bool (*send)(void *,const uint8_t *);
    bool (*load)(void *,sc_config_record *);
    bool (*save)(void *,sc_config_record *);
    bool (*protected_boot)(void *);
    void (*reset)(void *,bool);
    bool (*power)(void *,uint8_t,uint32_t);
    uint32_t (*rails)(void *,unsigned);
} sc_service_io;
typedef struct {
    sc_service_io io;
    uint8_t uid[12],prefix[12],prefix_mask,params,period;
    uint16_t session;
    bool boot,selected,updating,pending,cache_valid,reset_pending,reset_boot;
    uint32_t staged_inputs;
    bool inputs_staged;
    uint32_t touched,blink_until,reset_at,size,crc,offset,cursor;
    uint8_t request[8],reply[8];
} sc_service;
void sc_service_init(sc_service *,const sc_service_io *,const uint8_t uid[12],bool boot);
void sc_service_receive(sc_service *,const uint8_t *,uint32_t now);
void sc_service_tick(sc_service *,uint32_t now);
void sc_service_disable(sc_service *);
bool sc_service_active(const sc_service *);
bool sc_image_valid(const sc_service_io *);
uint32_t sc_get32(const uint8_t *);
#endif
