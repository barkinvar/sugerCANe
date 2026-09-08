#include "SensorCan.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <random>
static unsigned checks, inits, writes;
static int requestedApi, requestedTimeout, lastApi;
static bool available;
static frc::CANData packet{};
static uint8_t lastWrite[8];
#define CHECK(x)                                                               \
  do {                                                                         \
    assert(x);                                                                 \
    checks++;                                                                  \
  } while (0)
// Transport boundary substitute; compiled against the actual WPILib2026 CAN/hal
// headers. No claim that this executes the roboRIO native HAL.
namespace frc {
CAN::CAN(int device, int manufacturer, int type) {
  CHECK(device == 17 && manufacturer == 8 && type == 10);
  inits++;
}
bool CAN::ReadPacketTimeout(int api, int timeout, CANData *d) {
  requestedApi = api;
  requestedTimeout = timeout;
  *d = packet;
  return available;
}
void CAN::WritePacket(const uint8_t *d, int size, int api) {
  CHECK(size == 8);
  std::memcpy(lastWrite, d, 8);
  lastApi = api;
  writes++;
}
} // namespace frc
extern "C" void HAL_CleanCAN(HAL_CANHandle) {}
int main() {
  using namespace sensorcan;
  for (int id = 0; id < 64; id++)
    for (int api = 0; api < 1024; api++)
      CHECK(CanId(id, api) == (0x0a080000u | (static_cast<uint32_t>(api) << 6) |
                               static_cast<uint32_t>(id)));
  uint8_t d[8] = {1, 255, 5, 10, 3, 2, 7, 4};
  auto status = DecodeStatus(d, 8);
  CHECK(status && status->Input(1) && !status->Input(2) && status->Input(3) &&
        status->Configured() && status->ClockHealthy());
  for (int b = 0; b < 256; b++) {
    d[2] = static_cast<uint8_t>(b);
    CHECK(bool(DecodeStatus(d, 8)) == (b < 16));
  }
  d[2] = 5;
  for (unsigned len = 0; len < 12; len++)
    CHECK(bool(DecodeStatus(d, len)) == (len == 8));
  CHECK(!DecodeStatus(nullptr, 8));
  std::mt19937 gen(42);
  for (int i = 0; i < 10000; i++) {
    const uint32_t a = gen(), b = gen();
    for (unsigned k = 0; k < 4; k++) {
      d[k] = static_cast<uint8_t>(a >> (8 * k));
      d[k + 4] = static_cast<uint8_t>(b >> (8 * k));
    }
    auto c = DecodeCounts(d, 8);
    CHECK(c && c->first == a && c->second == b);
  }
  bool threw = false;
  try {
    SensorCan invalid(64);
  } catch (const std::invalid_argument &) {
    threw = true;
  }
  CHECK(threw && inits == 0);
  SensorCan sensor(17);
  CHECK(inits == 1);
  CHECK(!sensor.ReadStatus() && requestedTimeout == 100 &&
        requestedApi == kStatus);
  available = true;
  packet.length = 8;
  packet.timestamp = 1234;
  uint8_t valid[8] = {1, 255, 5, 10, 3, 2, 7, 4};
  std::memcpy(packet.data, valid, 8);
  auto sample = sensor.ReadStatus();
  CHECK(sample && sample->value.inputs == 5 && sample->timestampMillis == 1234);
  packet.length = 7;
  CHECK(!sensor.ReadStatus());
  packet.length = 8;
  packet.data[0] = 2;
  CHECK(!sensor.ReadStatus());
  available = false;
  CHECK(!sensor.ReadCounts12() && requestedTimeout == 350 &&
        requestedApi == kCounts12);
  CHECK(!sensor.ReadCounts34() && requestedApi == kCounts34);
  CHECK(!sensor.ReadDiagnostic() && requestedApi == kDiagnostic);
  CHECK(!sensor.ReadIdentity() && requestedTimeout == 1500);
  available = true;
  uint8_t ident[8] = {1, 0, 1, 0, 1, 17, 2, 1};
  std::memcpy(packet.data, ident, 8);
  CHECK(sensor.ReadIdentity());
  packet.data[5] = 18;
  CHECK(!sensor.ReadIdentity());
  sensor.ConfigureRuntime(9, 7, 3);
  const auto expected = Configuration(9, 7, 3);
  CHECK(lastApi == kConfigure && !std::memcmp(lastWrite, expected.data(), 8));
  sensor.ClearFaultsOnce(3);
  CHECK(lastApi == kClear && lastWrite[3] == 3 && writes == 2);
  for (int bad : {-1, 0, 4, 255}) {
    threw = false;
    try {
      sensor.ClearFaultsOnce(bad);
    } catch (const std::invalid_argument &) {
      threw = true;
    }
    CHECK(threw);
  }
  CHECK(writes == 2);
  std::printf("PASS C++ codec and driver: %u assertions; WPILib2026.2.1 "
              "headers, simulated transport\n",
              checks);
}
