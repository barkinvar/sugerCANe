# Why the small components are fitted

**Scope: Rev B.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/rev_b/README.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

This design has 34 capacitors. They are not all interchangeable filtering capacitors, and the present count is not proven to be the absolute minimum. This audit retains them until a reduction has measurement evidence.

| References | Job | Decision |
|---|---|---|
| C1 C2 C3 | Battery/input filtering | Keep |
| C4 C5 C13 | Buck output reservoir | Keep; C13 is a bench optimization candidate |
| C6 | Buck bootstrap | Keep |
| C7 C8 | 3.3V regulator input/output | Keep |
| C9 C10 | Battery sensor switch bypass/output | Keep |
| C11 C12 | 5V sensor switch bypass/output | Keep |
| C14 | Hardware fault timing | Keep |
| C15 C16 C17 | Boost output reservoir/bypass | Keep |
| C20 C21 C22 C23 | Microcontroller supply bypass | Keep |
| C24 | Microcontroller local bulk | Keep; bench optimization candidate |
| C25 C26 | Crystal load | Keep |
| C27 | Reset filtering | Keep |
| C28 C29 | Supply measurement filtering | Keep |
| C40 C41 | CAN supply bypass | Keep |
| C42 | CAN local bulk | Keep; bench optimization candidate |
| C50 | Comparator supply bypass | Keep |
| C101 C201 C301 | Sensor input filtering | Keep |

Several 100 nF capacitors share a supply net because they sit beside different chips or supply pins. Copper traces have inductance: one distant large capacitor cannot supply every fast local current pulse. Other capacitors are part of the converter, crystal, fault timer or input filter rather than rail bypass.

C13, C24 and C42 are candidates for a measured reduction experiment. Test supply extremes, both sensor rails loaded, startup, load steps, ripple, CAN traffic, reset behavior and temperature before approving their removal. No capacitor has been removed on the basis of appearance or a DC continuity check.

Most small resistors set input thresholds/hysteresis, sensor pull-up or pull-down current, regulator output voltage, fault current limits, safe enable states, ADC scaling or LED current. Many small black parts in the render are resistors, not capacitors. A factory-assembly variant can use lower-cost stocked equivalents without deleting these functions.

The larger simplification opportunities are the input-configuration network and the two-stage 5 V supply architecture. These require a circuit redesign and validation; changing to smaller package sizes alone does not remove their functions. See capacitor_audit.csv in the BOM folder for every capacitor and its reason.
