**Regional sourcing review — observations on 2026-09-07**

**Scope: Rev A.** [Revision overview](https://github.com/barkinvar/candi-clone/blob/main/REV_A.md) · [All revisions](https://github.com/barkinvar/candi-clone/blob/main/REVISIONS.md).

The delivered PCB BOM contains exact DigiKey order codes for every purchased component. The design favors familiar leaded packages, common passive sizes and active products. Global availability cannot be guaranteed from a catalog listing; regional storefronts can use the same warehouse, show different cached inventory, and apply different shipping/import conditions.

The following additional checks support the availability preference for several critical parts. They supplement the dated US BOM rather than replacing it with mixed currencies or inconsistent timestamps.

| Part | Additional source | Observed listing |
| --- | --- | --- |
| STM32F042K6T6 | [DigiKey India](https://www.digikey.in/en/products/detail/stmicroelectronics/STM32F042K6T6/4815294) | Indexed listing: 1,910 units, Active, ₹371.42 at quantity 1; 30-week manufacturer lead time. |
| STM32F042K6T6 | [Mouser UK](https://www.mouser.co.uk/ProductDetail/STMicroelectronics/STM32F042K6T6?qs=4b8myOmUP%252BsYBBEp2ZwbyQ%3D%3D) | Indexed product listing: 3,350 units. Separate older/newer search snapshots differed; direct-page access did not complete. |
| STM32F042K6T6 | [ST online store](https://estore.st.com/en/products/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus/stm32-mainstream-mcus/stm32f0-series/stm32f0x2/stm32f042k6.html) | Manufacturer's indexed listing marked the T6 tray variant in stock. |
| LMR51420XDDCR | [DigiKey Germany](https://www.digikey.de/en/products/detail/texas-instruments/LMR51420XDDCR/16705125) | Product page: 14,239 units, Active, €1.13 quantity 1 before VAT; 16-week manufacturer lead time. |
| TPS1H200AQDGNRQ1 | [DigiKey India](https://www.digikey.in/en/products/detail/texas-instruments/TPS1H200AQDGNRQ1/9593381) | Product page: 25,389 units, Active, ₹170.08 quantity 1; 16-week manufacturer lead time. |
| TCAN3413DR | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/texas-instruments/TCAN3413DR/22147199) | Product page: 4,877 units, Active, £1.38 quantity 1 before VAT; 16-week manufacturer lead time. |

These are availability signals across regional catalogs and more than one seller, not separate stock pools, reserved supply or a worldwide-delivery promise. Long factory lead times still matter if distributor stock is exhausted. For a team build, check the exact quantities in the destination-country cart before paying. No cart, purchase or supplier contact was made in this session.

The MCU and several power/protection ICs remain single-manufacturer devices. Generic package familiarity does not make every similarly named part interchangeable. In particular, keep the TPS2553 **-1** latch-off suffix, LMR51420 **X** 500 kHz variant, LM2901 **B** grade, the exact TPS1H200A pinout, 100 V bias diodes, capacitor DC-bias allowance, and the 5.00 mm terminal pitch. BOM alternative fields identify review candidates only.
