# Rev C Lite prototype quotation packet

Supply [Factory_BOM.csv](../bom/Factory_BOM.csv), [SMT positions](../output/assembly/positions_smd_top.csv), [all fitted positions](../output/assembly/positions_all_top.csv), the fabrication directory, schematic, assembly drawings and this guide. A [factory upload ZIP](../order/RevC_Lite_Factory_Upload.zip) collects them. This is a quotation/DFM packet, not an order already placed or a production-qualified release.

- 52 ×56 mm, 2-layer, 1.6 mm FR-4; nominal 1 oz copper. Quote ENIG for clean pogo contacts, solder mask and both silkscreens. Panel rails/fiducials/tooling are assembler-owned; do not move individual components or alter nets.
- **89 placements: 83 SMT plus six Weidmüller THT/THR terminals**, all inserted from the top. No purchased jumpers or shunts. Keep the seven solder selectors open unless a specific configuration is supplied in writing.
- Quote exact manufacturer part numbers. DigiKey stock/price observations are dated; the factory can source through authorized channels. No unverified LCSC code or promised JLCPCB basic-library status is supplied.
- Generic resistors/capacitors may have price advantages locally, but match value, tolerance, power, temperature coefficient, voltage, dielectric, DC-bias performance and package. Preserve the precision 5 V divider, 1206 pulldowns and three specific output capacitors unless reviewed.
- Do not silently substitute TPS2553 without the **-1 latch-off** behavior, the MCU package, CAN transceiver, crystal load, buck variant/operating mode, inductor family, or Weidmüller connector angle/footprint.
- Weidmüller 1824420000/1824430000 have horizontal /90 entry, 3.5 mm pole pitch, two legs per pole, 7 mm row spacing and 1.1 mm PCB drills. /135 and Phoenix PTSM are not drop-in substitutions.
- Review pick-and-place rotations against pin-one drawings, U3 exposed-pad soldering, connector polarity, stencil apertures and terminal solder fill. KiCad coordinates use X right, Y up from the top-left design origin; do not infer a factory-specific rotation convention without review.
- Factory programming, continuity, functional test, attrition and terminal hand soldering should be quoted explicitly. Use supplied firmware and a custom mapped TC2050 fixture. Unique device IDs are provisioned later over UART.

The **$43.90** figure is a dated quantity-one component estimate, not an assembled-board price. PCB, SMT setup, stencil, THT labor, programming/test, shipping, tax, component reels/attrition and MOQ must be added by a real quote. Fewer placements should reduce assembly work versus B/B-2, but no China factory quote has been obtained. Keeping specified terminals is likely to limit savings more than replacing a few inexpensive 0805 parts.
