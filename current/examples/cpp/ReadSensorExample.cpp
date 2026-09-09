#include "SensorCan12.h"
// Construct once as a subsystem member. Empty means unavailable or a reported fault.
std::optional<bool> ReadChannel1(sensorcan12::SensorCan12& board) {
  return board.ReadInput(1);
}
