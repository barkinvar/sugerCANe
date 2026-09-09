# Software input modes - Rev G

Each input has its own electronically controlled pull-up and pull-down; there are no input-bias jumpers or solder selectors. Select the mode in the desktop setup tool, CAN service CLI, or Java/C++ runtime API. This is an independent design with CANdi-like input choices; CTRE Phoenix and GrappleHook are not compatible protocols.

| Mode in setup tool | Electrical behavior | Default active condition | Typical use |
|---|---|---|---|
| `npn` | Pull toward 3.3 V through a diode and 1 kΩ | LOW | NPN / open collector sinking output |
| `pnp` | Pull toward ground through 10 kΩ | HIGH | PNP sourcing output |
| `push-pull` | Both bias switches off | HIGH | Actively driven 3.3 V, 5 V or industrial logic |
| `float` | Alternate pull-up/down to classify the source | DRIVEN | Slow contact / high-impedance diagnostics |
| `keeper` | Bias toward the last sampled level; starts LOW | HIGH | Hold a released line near its last logic level |

Active condition is independently selectable as `high`, `low`, `driven`, `floating`, `not-high`, or `not-low`. Inversion is applied afterward, then debounce. Normally leave the inversion mask at zero when using these active conditions. Firmware defaults to push-pull/HIGH on all channels; it does not guess a sensor type.

## Wiring and electrical limits

Power, ground and signal remain the three sensor-terminal contacts. Choose 5 V or 12 V sensor power with the separate removable power cap, with board power disconnected. These power caps and CAN termination are not input-bias settings. Keep a common signal ground.

The pull-up uses the internal **3.3 V rail regardless of sensor supply**. Its series diode blocks most current from a 5–30 V signal toward the MCU rail. The voltage-rated pull-down MOSFET switches a 10 kΩ resistor. The LM339LV comparator, protected divider and hysteresis still receive the field signal; no field-voltage connection goes directly to an STM32 GPIO. This remains digital sensing, not analog acquisition.

Targets: positive 0–30 V input, LOW ≤1.2 V, HIGH ≥2.4 V, ±0.1 V ground-offset allowance. The compatibility budget allows 100 µA OFF leakage for NPN or PNP sensors. NPN LOW residual must remain ≤1.2 V at up to approximately 3.5 mA sink current. Verify the exact sensor datasheet. A nominal 5 V push-pull signal works with bias off. A 3.3 V open-drain output may use NPN mode if it tolerates the board's pull-up while the sensor is unpowered; otherwise use an external pull-up to its own supply with onboard bias off.

Both switches default off through external gate resistors during reset and in the bootloader. Firmware applies saved modes during startup and suppresses measurements until input/rail settling completes. Removing a power cap does not disconnect SIGNAL; an enabled pull-up can inject current into an unpowered sensor. Set push-pull/bias-off before servicing an externally connected unpowered device. Reverse diode leakage is finite: the 10 kΩ 3.3 V rail bleed budgets about 0.61 V from the three bias diodes alone using the BAT46W 60°C specification. Charged sensor-rail capacitors can temporarily add current through the ADC dividers. This is not isolation or a whole-board unpowered-voltage guarantee.

## Floating detection and counts

Float mode waits at least 2 ms after each bias change. Two matching full pull-up/down pairs are required, so initial classification needs approximately 8 ms, plus configured debounce for subsequent logical changes. Input-level telemetry reports HIGH, LOW, FLOATING or UNKNOWN (unsettled). Drivers mark logical inputs unavailable while any channel is unsettled or either rail is unhealthy.

Probe transitions never enter the logical edge counter. Counters track debounced inactive-to-active transitions. They pause during rail faults and maintenance; startup/reconfiguration re-baselines without inventing an edge. Use float mode for slow signals, and qualify the real cable capacitance, noise and sensor leakage. Fast changes during a probe pair can be misclassified; fixed NPN/PNP/push-pull modes are preferable for ordinary sensing. This is not an encoder interface.

High impedance can mean a disconnected cable, an open contact, or the normal inactive state of an NPN/PNP output. Float detection cannot distinguish these causes. Keeper mode biases a released wire; it does not retain a value across reset or report a disconnection.

## Save an example configuration

From `current/`, after discovery and physical identification:

```sh
python host/can_service.py --bridge localhost:5810 configure \
  --uid UID --device 17 --invert 0 --debounce 2 \
  --modes npn,pnp,push-pull
```

Replace `UID` with the discovered 24-digit hexadecimal serial. The tool stages all three settings, commits with the ID/settings record, resets, and verifies persistent readback. If `--modes` is omitted, existing saved input settings are preserved. Optional `--active low,high,high` overrides the defaults. The desktop window offers the same choices independently for each channel.

Java `configureInputsRuntime(InputMode[], ActiveWhen[])` and C++ `ConfigureInputsRuntime(...)` apply volatile settings. Read back `inputState()` / `ReadInputState()` to verify the configuration word and classification; runtime CAN commands have no acknowledgment and do not write flash. Use CAN service to persist. See [wire format](CAN_PROTOCOL.md), [service](CAN_SERVICE.md) and [drivers](../examples/README.md).

Engineering checks and simulations do not qualify electrical behavior. Bench-test all modes across supply, temperature, cable length, hot-plug, sensor startup and robot vibration before deployment. See [validation](VALIDATION.md).
