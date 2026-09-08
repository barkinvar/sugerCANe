# Rev B-2 assembly and bring-up

For turnkey assembly, use [FACTORY_ORDER.md](FACTORY_ORDER.md). This guide covers bench assembly, inspection and rework of the same B-2 hardware.

**Scope: Rev B-2.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b2/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

Use the exact Rev B-2 BOM and board files together. Rev A has a different outline, connectors, comparator supply and power conversion. Do not mix the revisions.

1. Check the bare board, paste openings and drill sizes against the assembly drawing. Confirm that the terminal footprints have two plated holes per pole and that J8 has three nonplated alignment holes.
2. Fit the surface-mount parts with paste and controlled heatbed/reflow. Verify polarity for the input capacitor, diodes, LEDs and MOSFET. Confirm pin 1 on U3, U5 and U7. Inspect the exposed pad and thermal vias under U3, then inspect every MCU pin for bridges.
3. Fit the through-hole push-in terminals and 2 mm headers. JP302 pin 2 connects directly to the ground planes; preheat and sufficient iron power help wet this joint. Keep actuator and wire-entry directions consistent with the drawing. Clean and inspect joints before installing any shunts.
4. Leave power selectors and termination open for initial inspection. Check input-to-ground and 3.3 V-to-ground resistance for a hard short. Check that the two legs of each terminal pole are connected and adjacent poles are isolated.
5. Use a current-limited bench supply at J1, initially 12 V with no sensors. Verify protected input, approximately 3.97 V intermediate rail, 5 V internal rail and 3.3 V logic. With erased firmware/configuration, sensor power outputs should remain off.
6. Attach the correctly wired TC2050 adapter and SWD probe. Confirm target voltage/device identity, program the Rev B-2 image, and read back/verify flash. Keep probe power disconnected. Provision a unique CAN device ID with rails=0.
7. Power down, configure one sensor port, then reconnect power. Explicitly request the required rail. Verify voltage at the terminal before connecting the sensor. Test NPN/PNP or logic behavior against the selected threshold and bias.
8. Repeat for all three ports, then test combined loads at 5, 6.3, 12, 14.4, 20 and 22 V input. Confirm current limit, fault latch and explicit recovery with controlled loads. Measure temperatures and ripple rather than relying on touch or LED state.
9. Connect CAN with proper bus termination, verify all state bits/counters and diagnostics, and test communication loss, Broadcast Disable, watchdog reset and brownout recovery before robot use.

Do not change power or bias shunts while powered. Do not use a programmer's 3.3 V power output to feed the board. The delivered design has not been physically assembled; record measured results in the bench worksheet before considering it qualified.

Horizontal connector clearance: PCB remains 60 x 68 mm. Reserve an assembled envelope of 60 x 76.1 mm before adding cable bend/service space. The fixed housings project about 1 mm beyond each connector edge; the conservative actuator envelope extends 4.05 mm. Seated connector height is 8.5 mm, with 3.5 mm leads before trimming. Do not clamp or obstruct the front actuators.
