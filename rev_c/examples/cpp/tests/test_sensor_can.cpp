#include "SensorCanLiteCodec.h"
#include <cassert>
#include <iostream>
using namespace sensorcanlite;
int main() {
  std::array<uint8_t,8> d{2,254,5,2,3,31,7,1};
  auto s=DecodeStatus(d.data(),8);assert(s&&s->Input(1)&&!s->Input(2)&&s->Input(3)&&s->CanHealthy());
  for(int field:{0,2,3,4,5,6,7}) for(int value=0;value<256;value++) {
    auto t=d;t[field]=static_cast<uint8_t>(value);
    bool valid=field==0?value==2:field==4?value==3:field==5?value==31:field<4?value<8:value<16;
    assert(DecodeStatus(t.data(),8).has_value()==valid);
  }
  d={255,255,255,255,0,0,0,128};auto c=DecodeCounts(d.data(),8);
  assert(c&&c->first==0xffffffff&&c->second==0x80000000);assert(!DecodeCount3(d.data(),8));
  d[7]=0;assert(DecodeCount3(d.data(),8));
  d={255,255,255,255,128,127,7,3};assert(DecodeDiagnostic(d.data(),8)->transmitQueueDrops==0xffffffff);
  d[6]=8;assert(!DecodeDiagnostic(d.data(),8));
  d={2,0,3,0,3,20,2,7};assert(DecodeIdentity(d.data(),8));d[4]=2;assert(!DecodeIdentity(d.data(),8));
  assert((Configuration(7,100)==std::array<uint8_t,8>{0x53,0x43,2,7,100,0,0,0}));
  assert((Resume()==std::array<uint8_t,8>{0x53,0x43,2,0,0,0,0,0}));
  bool rejected=false;try {Configuration(8,2);}catch(const std::invalid_argument&){rejected=true;}assert(rejected);
  assert(!DecodeStatus(nullptr,8));assert(!DecodeStatus(d.data(),7));
  std::cout<<"PASS: Lite C++ protocol validation, unsigned counters and reserved fields\n";
}
