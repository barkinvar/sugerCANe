# Rev D-2 change scope

Preserve Rev D’s 52 × 64 mm, four-layer circuit, 300 mA shared 5 V / 12 V sensor rails, 3.3 V logic and hardware-4/protocol-v3 telemetry. Keep every component on the top side.

Replace JP101/JP201/JP301 solder power selectors with 2 mm three-pin through-hole headers and removable closed-top caps; preserve pin 1 = 5 V, pin 2 = port, pin 3 = 12 V. Bias and termination remain solder settings. Reroute only affected low-frequency sensor-area connections and refill ground planes; verify native and exported copper connectivity and clearances.

Substitute 16 ordinary 0805 resistors and eleven 100 nF 0805 bypass capacitors with documented equivalents. Preserve precision dividers, power resistors, bulk capacitance, converter compensation/protection and critical switching geometry. Source identical active MPNs from lower-cost distributor observations when available.

Factory assembles 98 top-side SMT parts. User fits six terminals and three headers and supplies three caps. All prices separate parts, order minimums and assembly assumptions. Deliver regenerated CAD/BOM/CPL/Gerber/STEP/PDF files, test evidence, source and factory packages. Physical fit, vibration and electrical qualification remain pending.

See [cost basis](docs/COST_REDUCTION.md), [assembly](docs/ASSEMBLY.md), [wiring](docs/WIRING.md) and [validation](docs/VALIDATION.md).

## CAN service implementation

Application 0.5.0, protected bootloader, UID-targeted CAN setup/updates, laptop tools, robot bridges and factory programming/acceptance scripts now use the existing PCB. The [optimization plan](docs/OPTIMIZATION_PLAN.md) records passed software tests and outstanding physical qualification/cost-quote gates. Rev D's earlier firmware is preserved.
