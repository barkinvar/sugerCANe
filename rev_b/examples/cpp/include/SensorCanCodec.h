#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <stdexcept>
namespace sensorcan {
constexpr int kManufacturer = 8, kDeviceType = 10, kStatus = 0x100,
              kCounts12 = 0x101, kCounts34 = 0x102, kDiagnostic = 0x110,
              kIdentity = 0x111, kConfigure = 0x200, kClear = 0x201;
inline int Range(int value, int low, int high) {
  if (value < low || value > high)
    throw std::invalid_argument("Sensor CAN parameter out of range");
  return value;
}
inline uint32_t CanId(int device, int api) {
  return (uint32_t{kDeviceType} << 24) | (uint32_t{kManufacturer} << 16) |
         (static_cast<uint32_t>(Range(api, 0, 1023)) << 6) |
         static_cast<uint32_t>(Range(device, 0, 63));
}
struct Status {
  uint8_t sequence, inputs, rawInputs, enabledRails, latchedFaults, flags,
      resetFlags;
  bool Input(int channel) const {
    return (inputs & (1u << (Range(channel, 1, 4) - 1))) != 0;
  }
  bool Configured() const { return (flags & 1) != 0; }
  bool ClockHealthy() const { return (flags & 2) != 0; }
  bool AdcHealthy() const { return (flags & 4) != 0; }
};
struct Counts {
  uint32_t first, second;
};
struct Diagnostic {
  uint16_t sensorBatteryMillivolts, sensor5Millivolts, transmitQueueDrops;
  uint8_t transmitErrors, receiveErrors;
};
struct Identity {
  uint8_t major, minor, patch, hardwareRevision, deviceId, debounceMillis,
      invertMask;
};
inline uint16_t U16(const uint8_t *d) {
  return static_cast<uint16_t>(d[0] | (uint16_t{d[1]} << 8));
}
inline uint32_t U32(const uint8_t *d) {
  return uint32_t{U16(d)} | (uint32_t{U16(d + 2)} << 16);
}
inline std::optional<Status> DecodeStatus(const uint8_t *d, std::size_t size) {
  if (!d || size != 8 || d[0] != 1 || (d[2] | d[3]) > 15 || (d[4] | d[5]) > 3 ||
      d[6] > 7 || d[7] > 15)
    return std::nullopt;
  return Status{d[1], d[2], d[3], d[4], d[5], d[6], d[7]};
}
inline std::optional<Counts> DecodeCounts(const uint8_t *d, std::size_t size) {
  if (!d || size != 8)
    return std::nullopt;
  return Counts{U32(d), U32(d + 4)};
}
inline std::optional<Diagnostic> DecodeDiagnostic(const uint8_t *d,
                                                  std::size_t size) {
  if (!d || size != 8)
    return std::nullopt;
  return Diagnostic{U16(d), U16(d + 2), U16(d + 4), d[6], d[7]};
}
inline std::optional<Identity> DecodeIdentity(const uint8_t *d,
                                              std::size_t size) {
  if (!d || size != 8 || d[0] != 1 || d[5] > 63 || d[6] < 1 || d[6] > 100 ||
      d[7] > 15)
    return std::nullopt;
  return Identity{d[1], d[2], d[3], d[4], d[5], d[6], d[7]};
}
inline std::array<uint8_t, 8> Configuration(int invert, int debounce,
                                            int rails) {
  return {0x53,
          0x43,
          1,
          static_cast<uint8_t>(Range(invert, 0, 15)),
          static_cast<uint8_t>(Range(debounce, 1, 100)),
          0,
          static_cast<uint8_t>(Range(rails, 0, 3)),
          0};
}
inline std::array<uint8_t, 8> ClearFaults(int mask) {
  return {0x53, 0x43, 1, static_cast<uint8_t>(Range(mask, 1, 3)), 0, 0, 0, 0};
}
} // namespace sensorcan
