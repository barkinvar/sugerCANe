# Purchasing and substitutions

The grouped BOM and DigiKey import CSV specify exact manufacturer and distributor part numbers. The estimate is **$59.30 per board in components**, using conservative single-unit prices, including ten 2 mm configuration shunts. PCB fabrication, stencil, tax, freight, tools, programming cable and assembly are excluded. This is a dated engineering estimate, not a reserved-stock quote.

Prices and inventory were observed on 2026-09-07/08. Regional DigiKey listings can expose different quantities, currencies and pack sizes. The selected parts favor established manufacturers and common leaded packages; global availability is a sourcing preference, not a guarantee. Recheck exact MPN, currency, cut-tape quantity, lifecycle and delivery location before placing an order.

The six horizontal push-in terminals total $11.25 at the observed quantity-one prices. Selected parts are Weidmuller LSF-SMT 3.50/02/90 3.5SN BK TU (1824420000, $1.54, 12,805 observed) and LSF-SMT 3.50/03/90 3.5SN BK TU (1824430000, $2.21, 1,698 observed). US DigiKey pages were checked on 2026-09-08. An older cached result showed the two-pole part out of stock; the freshly opened product page supplied the later observation. These are dated observations, not reserved stock. Each pole has two solder legs, 7 mm apart; this is not the previous /135 footprint.

A physically similar push-in connector is not automatically a substitute. Check entry direction, body envelope, pin rows, hole pitch, lead length, current rating and actuator clearance. Screw terminals are not included. The chosen terminals accept bare wire; use the manufacturer's 8 mm strip length and wire preparation instructions. For this prototype, 20–22 AWG is a practical assembly choice within the selected manufacturer's range.

For passive substitutions, preserve value, tolerance, temperature coefficient, power/voltage rating, dielectric and footprint. Retain the 0.1% divider resistors, higher-power 2010 pull-down resistors, 50 V input capacitor and specified effective output capacitance. MLCC nameplate capacitance alone does not establish capacitance at DC bias.

Do not substitute a comparator by pinout alone. Rev B supplies LM339LV from 3.3 V and relies on its input range. Power switches, converter suffixes, inductors and crystal/load capacitors require a new electrical review when substituted. TPS2553DBVR-1 is the latched variant.

External accessories are separate: a TC2050-IDC-NL cable, suitable SWD probe and custom adapter matching the documented pin map. The cable's mechanical fit does not imply a standard ARM electrical pinout. No US cable price is included because only a regional price was reliably observed. Insulated mounting hardware and robot-side fused power wiring are also separate.

Sources: [two-pole manufacturer drawing](https://datasheet.weidmueller.com/pdf/en/1824420000/scope/1/), [three-pole manufacturer drawing](https://datasheet.weidmueller.com/pdf/en/1824430000/scope/1/), [three-pole DigiKey listing](https://www.digikey.in/en/products/detail/weidm%C3%BCller/1824430000/2410727), [Tag-Connect cable](https://www.tag-connect.com/product/tc2050-idc-nl-10-pin-no-legs-cable-with-ribbon-connector). Per-part links and observation dates are in the BOM.
