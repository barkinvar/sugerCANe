#include "SensorCanLite.h"
// Construct SensorCanLite once as a subsystem member. Empty means unavailable.
// This is a signal sample; Rev C cannot establish whether sensor power is healthy.
std::optional<bool> ReadChannel1(sensorcanlite::SensorCanLite& board) {
  const auto sample=board.ReadStatus();
  if (!sample || !sample->value.Configured() || !sample->value.ClockHealthy() || !sample->value.CanHealthy())
    return std::nullopt;
  return sample->value.Input(1);
}
