#include "SensorCan.h"
// Configure channel1 on the battery sensor rail, with logical TRUE meaning
// piece present. Construct once as a subsystem member; choose a unique device
// ID through the UART tool.
bool IntakeMayRun(sensorcan::SensorCan &sensor) {
  const auto diagnostic = sensor.ReadDiagnostic();
  // Example10V-minimum sensor: budget drop and diagnostic error; measure yours.
  if (!diagnostic || diagnostic->value.sensorBatteryMillivolts < 11000)
    return false;
  const auto sample = sensor.ReadStatus();
  if (!sample)
    return false;
  const auto &s = sample->value;
  return s.Configured() && s.ClockHealthy() && s.AdcHealthy() &&
         (s.enabledRails & 2) && !(s.latchedFaults & 2) && !s.Input(1);
}
