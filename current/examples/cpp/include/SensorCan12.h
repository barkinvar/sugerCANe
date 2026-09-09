#pragma once
#include "SensorCan12Codec.h"
#include <frc/CAN.h>
namespace sensorcan12 {
template <typename T> struct Sample {
  T value;
  uint64_t timestampMillis;
};
/** Original FRC Sensor CAN protocol, for WPILib2026. Reads never enable sensor
 * power. */
class SensorCan12 {
public:
  explicit SensorCan12(int deviceId)
      : deviceId_(Range(deviceId, 0, 63)),
        can_(deviceId_, kManufacturer, kDeviceType) {}
  std::optional<Sample<InputState>> ReadInputState() {
    return Read<InputState>(kInputState,100,DecodeInputState);
  }
  void ConfigureInputsRuntime(const std::array<InputMode,3>& modes,const std::array<ActiveWhen,3>& active) {
    const auto d=InputConfiguration(modes,active);can_.WritePacket(d.data(),8,kInputConfig);
  }
  std::optional<Sample<Status>> ReadStatus() {
    return Read<Status>(kStatus, 100, DecodeStatus);
  }
  std::optional<bool> ReadInput(int channel) {
    Range(channel, 1, 3);
    const auto s = ReadStatus();
    if (!s || !s->value.Usable()) return std::nullopt;
    return s->value.Input(channel);
  }
  std::optional<Sample<Counts>> ReadCounts12() {
    return Read<Counts>(kCounts12, 350, DecodeCounts);
  }
  std::optional<Sample<Counts>> ReadCount3() {
    return Read<Counts>(kCount3, 350, DecodeCount3);
  }
  std::optional<Sample<Diagnostic>> ReadDiagnostic() {
    return Read<Diagnostic>(kDiagnostic, 350, DecodeDiagnostic);
  }
  std::optional<Sample<Identity>> ReadIdentity() {
    auto s = Read<Identity>(kIdentity, 1500, DecodeIdentity);
    return s && s->value.deviceId == deviceId_ ? s : std::nullopt;
  }
  /** Explicit volatile input settings; hardware power is independent. */
  void ConfigureRuntime(int invert, int debounceMillis) {
    const auto d = Configuration(invert, debounceMillis);
    can_.WritePacket(d.data(), 8, kConfigure);
  }
  /** Explicit resume only. Never call this from a periodic read loop. */
  void ResumeTelemetry() {
    const auto d = Resume();
    can_.WritePacket(d.data(), 8, kResume);
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
} // namespace sensorcan12
