#pragma once
#include "SensorCanCodec.h"
#include <frc/CAN.h>
namespace sensorcan {
template <typename T> struct Sample {
  T value;
  uint64_t timestampMillis;
};
/** Original FRC Sensor CAN protocol, for WPILib2026. Reads never enable sensor
 * power. */
class SensorCan {
public:
  explicit SensorCan(int deviceId)
      : deviceId_(Range(deviceId, 0, 63)),
        can_(deviceId_, kManufacturer, kDeviceType) {}
  std::optional<Sample<Status>> ReadStatus() {
    return Read<Status>(kStatus, 100, DecodeStatus);
  }
  std::optional<Sample<Counts>> ReadCounts12() {
    return Read<Counts>(kCounts12, 350, DecodeCounts);
  }
  std::optional<Sample<Counts>> ReadCounts34() {
    return Read<Counts>(kCounts34, 350, DecodeCounts);
  }
  std::optional<Sample<Diagnostic>> ReadDiagnostic() {
    return Read<Diagnostic>(kDiagnostic, 350, DecodeDiagnostic);
  }
  std::optional<Sample<Identity>> ReadIdentity() {
    auto s = Read<Identity>(kIdentity, 1500, DecodeIdentity);
    return s && s->value.deviceId == deviceId_ ? s : std::nullopt;
  }
  /** Explicit volatile setting. Bits1=5V,2=VBAT; does not change stored boot
   * settings. */
  void ConfigureRuntime(int invert, int debounceMillis, int railMask) {
    const auto d = Configuration(invert, debounceMillis, railMask);
    can_.WritePacket(d.data(), 8, kConfigure);
  }
  /** Explicit single retry, only after checking wiring and >=100ms off time. */
  void ClearFaultsOnce(int mask) {
    const auto d = ClearFaults(mask);
    can_.WritePacket(d.data(), 8, kClear);
  }

private:
  int deviceId_;
  frc::CAN can_;
  template <typename T, typename Decoder>
  std::optional<Sample<T>> Read(int api, int timeout, Decoder decoder) {
    frc::CANData d{};
    if (!can_.ReadPacketTimeout(api, timeout, &d) || d.length != 8)
      return std::nullopt;
    auto value = decoder(d.data, 8);
    if (!value)
      return std::nullopt;
    return Sample<T>{*value, d.timestamp};
  }
};
} // namespace sensorcan
