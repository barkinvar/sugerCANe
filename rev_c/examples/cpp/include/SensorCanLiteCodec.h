#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <stdexcept>
namespace sensorcanlite {
constexpr int kManufacturer = 8, kDeviceType = 10, kStatus = 0x120,
              kCounts12 = 0x121, kCount3 = 0x122, kDiagnostic = 0x130,
              kIdentity = 0x131, kConfigure = 0x220, kResume = 0x221;
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
  uint8_t sequence, inputs, rawInputs, channels, capabilities, flags,
      resetFlags;
  bool Input(int channel) const {
    return (inputs & (1u << (Range(channel, 1, 3) - 1))) != 0;
  }
  bool Configured() const { return (flags & 1) != 0; }
  bool ClockHealthy() const { return (flags & 2) != 0; }
  bool CanHealthy() const { return (flags & 4) != 0 && !(flags & 8); }
};
struct Counts {
  uint32_t first, second;
};
struct Diagnostic {
  uint32_t transmitQueueDrops;
  uint8_t transmitErrors, receiveErrors, lastErrorCode, flags;
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
  if (!d || size != 8 || d[0] != 2 || (d[2] | d[3]) > 7 || d[4] != 3 || d[5] != 31 ||
      d[6] > 15 || d[7] > 15)
    return std::nullopt;
  return Status{d[1], d[2], d[3], d[4], d[5], d[6], d[7]};
}
inline std::optional<Counts> DecodeCounts(const uint8_t *d, std::size_t size) {
  if (!d || size != 8)
    return std::nullopt;
  return Counts{U32(d), U32(d + 4)};
}
inline std::optional<Counts> DecodeCount3(const uint8_t *d, std::size_t size) {
  const auto c = DecodeCounts(d, size);
  return c && c->second == 0 ? c : std::nullopt;
}
inline std::optional<Diagnostic> DecodeDiagnostic(const uint8_t *d,
                                                  std::size_t size) {
  if (!d || size != 8 || d[6] > 7 || d[7] > 3)
    return std::nullopt;
  return Diagnostic{U32(d), d[4], d[5], d[6], d[7]};
}
inline std::optional<Identity> DecodeIdentity(const uint8_t *d,
                                              std::size_t size) {
  if (!d || size != 8 || d[0] != 2 || d[5] > 63 || d[6] < 1 || d[6] > 100 ||
      d[7] > 7 || d[4] != 3)
    return std::nullopt;
  return Identity{d[1], d[2], d[3], d[4], d[5], d[6], d[7]};
}
inline std::array<uint8_t, 8> Configuration(int invert, int debounce) {
  return {0x53, 0x43, 2, static_cast<uint8_t>(Range(invert, 0, 7)),
          static_cast<uint8_t>(Range(debounce, 1, 100)), 0, 0, 0};
}
inline std::array<uint8_t, 8> Resume() { return {0x53, 0x43, 2, 0, 0, 0, 0, 0}; }
} // namespace sensorcanlite
