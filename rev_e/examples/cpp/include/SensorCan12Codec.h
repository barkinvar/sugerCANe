#pragma once
#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <stdexcept>
namespace sensorcan12 {
constexpr int kManufacturer = 8, kDeviceType = 10, kStatus = 0x120,
              kCounts12 = 0x121, kCount3 = 0x122, kDiagnostic = 0x130,
              kIdentity = 0x131, kConfigure = 0x220, kResume = 0x221, kInputState = 0x132, kInputConfig = 0x222;
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
  bool Rail12Good() const { return (flags & 16) != 0; }
  bool Rail5NoFault() const { return (flags & 32) != 0; }
  bool PowerHealthy() const { return Rail12Good() && Rail5NoFault(); }
  bool Usable() const { return Configured() && ClockHealthy() && CanHealthy() && PowerHealthy() && InputsSettled(); }
  bool InputsSettled() const { return (flags & 64) != 0; }
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
  if (!d || size != 8 || d[0] != 4 || (d[2] | d[3]) > 7 || d[4] != 3 || d[5] != 127 ||
      d[6] > 127 || d[7] > 15)
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
  if (!d || size != 8 || d[0] != 4 || d[5] > 63 || d[6] < 1 || d[6] > 100 ||
      d[7] > 7 || d[4] != 5)
    return std::nullopt;
  return Identity{d[1], d[2], d[3], d[4], d[5], d[6], d[7]};
}
enum class InputMode { Off, PullHigh, PullLow, FloatDetect, BusKeeper };
enum class ActiveWhen { High, Low, Driven, Floating, NotHigh, NotLow };
enum class InputLevel { Low, High, Floating, Unknown };
struct InputState {
  uint8_t valid, floating, high; uint32_t configuration;
  InputLevel Level(int channel) const {
    const auto bit=1u<<(Range(channel,1,3)-1);
    return !(valid&bit) ? InputLevel::Unknown : (floating&bit) ? InputLevel::Floating :
           (high&bit) ? InputLevel::High : InputLevel::Low;
  }
};
inline bool ValidInputs(uint32_t word) {
  if(word>>18) return false;
  for(unsigned i=0;i<3;i++) if(((word>>(3*i))&7)>4 || ((word>>(9+3*i))&7)>5) return false;
  return true;
}
inline std::optional<InputState> DecodeInputState(const uint8_t *d,std::size_t size) {
  if(!d || size!=8 || d[0]!=4 || (d[1]|d[2]|d[3])>7 || (d[2]&d[3]) || !ValidInputs(U32(d+4))) return std::nullopt;
  return InputState{d[1],d[2],d[3],U32(d+4)};
}
inline std::array<uint8_t,8> InputConfiguration(const std::array<InputMode,3>& modes,const std::array<ActiveWhen,3>& active) {
  uint32_t word=0;
  for(unsigned i=0;i<3;i++) word |= static_cast<uint32_t>(Range(static_cast<int>(modes[i]),0,4))<<(3*i) |
    static_cast<uint32_t>(Range(static_cast<int>(active[i]),0,5))<<(9+3*i);
  return {0x53,0x43,4,0,static_cast<uint8_t>(word),static_cast<uint8_t>(word>>8),static_cast<uint8_t>(word>>16),0};
}
inline std::array<uint8_t, 8> Configuration(int invert, int debounce) {
  return {0x53, 0x43, 4, static_cast<uint8_t>(Range(invert, 0, 7)),
          static_cast<uint8_t>(Range(debounce, 1, 100)), 0, 0, 0};
}
inline std::array<uint8_t, 8> Resume() { return {0x53, 0x43, 4, 0, 0, 0, 0, 0}; }
} // namespace sensorcan12
