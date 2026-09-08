package frc.robot.sensors;

/** Example policy only: adapt channel, polarity, rail selection, and motor control to your robot. */
public final class IntakeSensorExample implements AutoCloseable {
  private final SensorCan sensor = new SensorCan(20);

  /**
   * Call from robot periodic. Channel 1 must be configured so TRUE means a detected game piece.
   * This example uses a sensor requiring at least10V on the battery rail (mask2).
   * The11V diagnostic threshold budgets wiring drop and measurement error; characterize your sensor.
   */
  public boolean intakeMayRun() {
    var diagnostic = sensor.diagnostic();
    if (diagnostic.isEmpty() || diagnostic.get().value().sensorBatteryMillivolts() < 11000)
      return false;
    return sensor.status().map(sample -> {
      var status = sample.value();
      return status.configured() && status.clockHealthy() && status.adcHealthy()
        && (status.enabledRails() & 2) != 0 && (status.latchedFaults() & 2) == 0
        && !status.input(1);
    }).orElse(false);
  }
  @Override public void close() { sensor.close(); }
}
