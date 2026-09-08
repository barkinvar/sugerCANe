# Rev C Lite purchasing

89 fitted components, 42 exact purchase MPNs, **$43.90** on a dated quantity-one basis. There are no purchased shunts. [Grouped BOM](BOM_grouped.csv), [per-reference BOM](BOM_per_reference.csv), [DigiKey import](DigiKey_import.csv), [factory BOM](Factory_BOM.csv).

Prices/stock are web observations from September 7–8, 2026, with inherited observations explicitly retained in the catalog. They are not reserved inventory or a live quotation. DigiKey pages and indexed substitute listings can differ; reprice the import/cart at purchase. Quantity breaks, PCB, assembly, shipping, tax and attrition are excluded. Other distributors or factories may offer lower prices, but no factory quotation has been obtained.

The design uses common 0805 resistors/capacitors, a leaded STM32 MCU, SOIC devices and standard diode packages to support multiple sourcing options. Availability of the selected MCU, power switches and exact Weidmüller connectors must still be checked. “Globally available” is a sourcing preference, not a guarantee.

R1/R2 are 0.1%, 25 ppm/°C. R109/R209/R309 are 1206, 0.25 W. Keep the three CL31A226KAHNNNE output capacitors unless an alternative's DC-bias behavior is reviewed. Match package and tolerance as well as nominal value. Use TPS2553DBVR-1 for latch-off behavior. See [factory substitution policy](../docs/FACTORY_ORDER.md).
