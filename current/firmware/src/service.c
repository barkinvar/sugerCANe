#include "service.h"
#include <string.h>
uint32_t sc_get32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static bool image_crc(const sc_service_io *io,uint32_t size,uint32_t *out) {
    uint32_t crc=0xffffffffu;
    uint8_t buf[32];
    for(uint32_t off=0;off<size;) {
        uint32_t n=size-off;if(n>sizeof(buf))n=sizeof(buf);
        if(!io->read(io->ctx,SC_APP_BASE+off,buf,n))return false;
        for(uint32_t k=0;k<n;k++) {
            crc^=buf[k];
            for(unsigned b=0;b<8;b++)crc=(crc>>1)^((0u-(crc&1u))&0xedb88320u);
        }
        off+=n;
    }
    *out=~crc;return true;
}
static bool vectors_valid(const sc_service_io *io,uint32_t size) {
    uint8_t v[8];
    if(size<192 || size>SC_APP_SIZE || (size&3u) || !io->read(io->ctx,SC_APP_BASE,v,8))return false;
    uint32_t sp=sc_get32(v),pc=sc_get32(v+4);
    return sp>=0x20000100u && sp<=0x20001800u && !(sp&7u) && (pc&1u) &&
           (pc&~1u)>=SC_APP_BASE+192u && (pc&~1u)<SC_APP_BASE+size;
}
bool sc_image_valid(const sc_service_io *io) {
    uint32_t m[6],crc;
    return io->read(io->ctx,SC_MANIFEST,m,sizeof(m)) && m[0]==SC_IMAGE_MAGIC &&
        m[3]==SC_IMAGE_TAG && m[4]==sc_crc32(m,16) && m[5]==SC_IMAGE_COMMIT &&
        vectors_valid(io,m[1]) && image_crc(io,m[1],&crc) && crc==m[2];
}
void sc_service_init(sc_service *s,const sc_service_io *io,const uint8_t uid[12],bool boot) {
    memset(s,0,sizeof(*s));s->io=*io;memcpy(s->uid,uid,12);s->boot=boot;s->period=10;
}
bool sc_service_active(const sc_service *s){return s->session!=0;}
void sc_service_disable(sc_service *s) {
    s->reset_pending=false;s->session=0;s->selected=false;s->pending=false;s->cache_valid=false;s->updating=false;s->params=0;s->inputs_staged=false;
}
void sc_service_tick(sc_service *s,uint32_t now) {
    if(s->session && now-s->touched>=SC_LEASE_MS)sc_service_disable(s);
    if(s->pending && s->io.send(s->io.ctx,s->reply))s->pending=false;
    if(s->reset_pending && (uint32_t)(now-s->reset_at)<0x80000000u) {
        s->reset_pending=false;s->io.reset(s->io.ctx,s->reset_boot);
    }
}
static bool matches(sc_service *s,uint32_t bits) {
    if(bits>96 || s->prefix_mask!=7)return false;
    for(uint32_t n=0;n<bits;n++)if(((s->uid[n/8]^s->prefix[n/8])&(1u<<(7u-n%8u)))!=0)return false;
    return true;
}
static void answer(sc_service *s,const uint8_t *d,uint8_t error,uint32_t value) {
    memcpy(s->request,d,8);s->reply[0]=d[0]|(error?0xc0u:0x80u);
    memcpy(s->reply+1,d+1,3);sc_put_u32(s->reply+4,error?error:value);
    s->cache_valid=true;s->pending=true;
}
void sc_service_receive(sc_service *s,const uint8_t *d,uint32_t now) {
    uint8_t op=d[0];uint16_t token=(uint16_t)(d[2]|((uint16_t)d[3]<<8));
    uint32_t value=sc_get32(d+4),result=0;uint8_t error=0;
    sc_service_tick(s,now);
    if(s->reset_pending)return;
    if(op==SC_OPEN) {
        if(!token || value!=SC_SERVICE_MAGIC)return;
        if(s->session!=token) {
            sc_service_disable(s);s->session=token;s->prefix_mask=0;
        }
        s->touched=now;answer(s,d,0,SC_SERVICE_MAGIC);return;
    }
    if(!s->session || token!=s->session)return;
    s->touched=now;
    /* Replay only an exact immediately previous transaction, never another payload. */
    if(s->cache_valid && !memcmp(s->request,d,8)){s->pending=true;return;}
    if(op>=SC_PREFIX0 && op<=SC_PREFIX2) {
        unsigned n=op-SC_PREFIX0;memcpy(s->prefix+4*n,d+4,4);
        s->prefix_mask|=(uint8_t)(1u<<n);s->selected=false;s->inputs_staged=false;s->cache_valid=false;return;
    }
    if(op==SC_PROBE) {
        s->selected=matches(s,value)&&value==96;s->cache_valid=false;
        if(!s->selected)s->inputs_staged=false;
        if(matches(s,value))answer(s,d,0,1);
        return;
    }
    if(op==SC_CLOSE) {sc_service_disable(s);return;}
    if(!s->selected)return;
    if(op==SC_INFO) {
        sc_config_record cfg={0};bool configured=s->io.load(s->io.ctx,&cfg);
        switch(value) {
        case 0:result=1u|((uint32_t)s->boot<<8)|((uint32_t)configured<<9)|
                      ((uint32_t)s->io.protected_boot(s->io.ctx)<<10)|(9u<<16)|(8u<<24);break;
        case 1:result=(configured?cfg.device_id:255u)|((uint32_t)cfg.invert_mask<<8)|
                       ((uint32_t)(configured?cfg.debounce_ms:2u)<<16)|((uint32_t)s->period<<24);break;
        case 2:result=s->boot?0x00010100u:0x00000900u;break;
        case 10:case 11:
            if(s->boot || !s->io.rails)error=SC_BAD_STATE;
            else result=s->io.rails(s->io.ctx,value-10);
            break;
        case 3:result=s->offset;break;
        case 9:result=configured?cfg.input_config:0;break;
        case 4:result=SC_APP_SIZE;break;
        case 5:result=sc_image_valid(&s->io);break;
        case 6:case 7:case 8:result=sc_get32(s->uid+4*(value-6));break;
        default:error=SC_BAD_ARGUMENT;
        }
    } else if(op==SC_BLINK) {s->blink_until=now+3000;}
    else if(op==SC_RATE) {
        if(value!=10 && value!=20 && value!=50)error=SC_BAD_ARGUMENT;
        else {s->period=(uint8_t)value;result=value;}
    } else if(op==SC_INPUTS) {
        if(!sc_input_config_valid(value))error=SC_BAD_ARGUMENT;
        else{s->staged_inputs=value;s->inputs_staged=true;result=value;}
    } else if(op==SC_POWER) {
        if(!value || value>3)error=SC_BAD_ARGUMENT;
        else if(s->boot || !s->io.power || !s->io.power(s->io.ctx,(uint8_t)value,now))error=SC_BAD_STATE;
        else result=value;
    } else if(op==SC_SAVE) {
        sc_config_record cfg={0};cfg.device_id=d[4];cfg.invert_mask=d[5];cfg.debounce_ms=d[6];
        if(d[7] || cfg.device_id>63 || cfg.invert_mask>7 || !cfg.debounce_ms || cfg.debounce_ms>100)error=SC_BAD_ARGUMENT;
        else {
            sc_config_record old={0};
            bool loaded=s->io.load(s->io.ctx,&old);
            cfg.input_config=s->inputs_staged?s->staged_inputs:(loaded?old.input_config:0);
            bool same=loaded && old.input_config==cfg.input_config && old.device_id==cfg.device_id &&
                old.invert_mask==cfg.invert_mask && old.debounce_ms==cfg.debounce_ms;
            if(!same && !s->io.save(s->io.ctx,&cfg))error=SC_FLASH_ERROR;
            else {result=value;s->reset_pending=true;s->reset_boot=s->boot;s->reset_at=now+50;}
        }
    } else if(op==SC_BOOT || op==SC_RUN) {
        if(value)error=SC_BAD_ARGUMENT;
        else if(op==SC_RUN && !sc_image_valid(&s->io))error=SC_BAD_IMAGE;
        else if(op!=SC_BOOT || !s->boot) {
            s->reset_pending=true;s->reset_boot=op==SC_BOOT;s->reset_at=now+50;
        }
    } else if(!s->boot)error=SC_BAD_STATE;
    else if(op==SC_SIZE) {
        if(value<192 || value>SC_APP_SIZE || (value&3u))error=SC_BAD_ARGUMENT;
        else{s->size=value;s->params=1;s->updating=false;result=value;}
    } else if(op==SC_CRC) {
        if(s->params!=1)error=SC_BAD_STATE;
        else{s->crc=value;s->params=3;result=value;}
    } else if(op==SC_BEGIN) {
        if(value!=SC_IMAGE_TAG || s->params!=3)error=SC_BAD_ARGUMENT;
        else if(!s->io.protected_boot(s->io.ctx))error=SC_NOT_PROTECTED;
        else {
            uint32_t marker=0;
            if(!s->io.erase(s->io.ctx,SC_MANIFEST) ||
               !s->io.read(s->io.ctx,SC_MANIFEST+20,&marker,4) || marker!=0xffffffffu)error=SC_FLASH_ERROR;
            else{s->offset=0;s->cursor=UINT32_MAX;s->updating=true;}
        }
    } else if(op==SC_OFFSET) {
        if(!s->updating || (value!=s->offset && !(s->offset>=4 && value==s->offset-4)))error=SC_BAD_STATE;
        else{s->cursor=value;result=value;}
    } else if(op==SC_DATA) {
        if(!s->updating || s->cursor>=s->size)error=SC_BAD_STATE;
        else if(s->cursor!=s->offset) {
            uint32_t old=0;
            if(s->offset<4 || s->cursor!=s->offset-4 || !s->io.read(s->io.ctx,SC_APP_BASE+s->cursor,&old,4) || old!=value)error=SC_BAD_STATE;
            else result=s->offset;
        } else {
            bool ok=true;uint32_t readback=0;
            if(!(s->offset%1024))ok=s->io.erase(s->io.ctx,SC_APP_BASE+s->offset);
            if(ok)ok=s->io.write(s->io.ctx,SC_APP_BASE+s->offset,d+4,4);
            if(ok)ok=s->io.read(s->io.ctx,SC_APP_BASE+s->offset,&readback,4)&&readback==value;
            if(!ok){error=SC_FLASH_ERROR;s->updating=false;}
            else {s->offset+=4;result=s->offset;}
        }
    } else if(op==SC_FINISH) {
        uint32_t crc=0;
        if(value || !s->updating || s->offset!=s->size)error=SC_BAD_STATE;
        else if(!vectors_valid(&s->io,s->size) || (!image_crc(&s->io,s->size,&crc) || crc!=s->crc))error=SC_BAD_IMAGE;
        else {
            uint32_t m[6]={SC_IMAGE_MAGIC,s->size,s->crc,SC_IMAGE_TAG,0,SC_IMAGE_COMMIT};
            m[4]=sc_crc32(m,16);
            if(!s->io.write(s->io.ctx,SC_MANIFEST,m,20) ||
               !s->io.write(s->io.ctx,SC_MANIFEST+20,m+5,4) || !sc_image_valid(&s->io))error=SC_FLASH_ERROR;
            else {s->updating=false;result=s->crc;}
        }
    } else error=SC_BAD_ARGUMENT;
    answer(s,d,error,result);
}
