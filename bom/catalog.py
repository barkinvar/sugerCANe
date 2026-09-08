"""Selected orderable parts and dated distributor observations.
Observations are from DigiKey catalog pages/search index accessed 2026-09-07;
quantities/prices are indicative, not an inventory reservation or live quote.
"""
from urllib.parse import quote
CATALOG={}
def add(mpn,mfr,sku='',product_path='',stock=None,price=None,note='',alt=''):
 CATALOG[mpn]={'mpn':mpn,'manufacturer':mfr,'digikey_sku':sku,
  'digikey_url':'https://www.digikey.com/en/products/detail/'+product_path if product_path else 'https://www.digikey.com/en/products?keywords='+quote(mpn,safe=''),
  'reported_stock':stock,'unit_price_usd_qty1':price,'unit_price_usd_qty10':None,'checked_date':'2026-09-07',
  'availability_note':note,'alternative_mpn':alt,
  'evidence_kind':'DigiKey catalog observation; stock/price must be reconfirmed before order' if stock is not None else 'Selected catalog part; exact stock/price verification pending'}
add('AO4485','Alpha & Omega Semiconductor','785-1551-1-ND','alpha-omega-semiconductor-inc/AO4485/3152385',64905,1.51,'40V P-channel,SOIC8,20mohm max at-4.5V gate. Datasheet pin mapping checked.',alt='DMP4025LSS-13; FDS4685 (same pin arrangement; recheck Rds,SOA and stock)')
add('MMSZ12T1G','onsemi','MMSZ12T1GOSCT-ND','onsemi/MMSZ12T1G/1139870',34429,.17,'12V,5%,500mW,SOD123 gate-source clamp; cathode to protected supply.')
add('STM32F042K6T6','STMicroelectronics','497-14647-ND','stmicroelectronics/STM32F042K6T6/4815294',3072,4.34,alt='STM32F042K6T6TR (same die/package, reel suffix)')
add('LMR51420XDDCR','Texas Instruments','296-LMR51420XDDCRCT-ND','texas-instruments/LMR51420XDDCR/16705125',14239,1.32)
add('TCAN3413DR','Texas Instruments','296-TCAN3413DRCT-ND','texas-instruments/TCAN3413DR/22147484',5237,1.87)
add('AP2112K-3.3TRG1','Diodes Incorporated','AP2112K-3.3TRG1DICT-ND','diodes-incorporated/AP2112K-3-3TRG1/4470746',159040,.28)
add('TPS2553DBVR-1','Texas Instruments','296-39380-1-ND','texas-instruments/TPS2553DBVR-1/2047901',5463,1.06)
add('TPS1H100AQPWPRQ1','Texas Instruments','296-42052-1-ND','texas-instruments/TPS1H100AQPWPRQ1/5226725',17975,None,'Stock observed on DigiKey Canada; confirm US price.')
add('LM2901BIDR','Texas Instruments','296-LM2901BIDRCT-ND','texas-instruments/LM2901BIDR/21442011',4028,None,'Use B-grade comparator; older LM2901 variants have different error bounds.')
add('BAT46W-E3-18','Vishay','BAT46W-E3-18GICT-ND','vishay-general-semiconductor-diodes-division/BAT46W-E3-18/4826890',19871,None,'100V reverse blocking; do not substitute 30V BAT54.')
add('SRP7028A-100M','Bourns','SRP7028A-100MCT-ND','bourns-inc/SRP7028A-100M/4876733',9366,1.10,'Active 10uH, 3.5A RMS, 6A saturation. SRP7030 is NRND and excluded.')
add('ABM3B-8.000MHZ-B2-T','Abracon','535-9720-1-ND','abracon-llc/ABM3B-8-000MHZ-B2-T/1873166',70541,.76,'18pF load, ESR<=200ohm, 20ppm initial/50ppm stability, -20..70C.')
add('ESD2CAN24DBZRQ1','Texas Instruments','296-ESD2CAN24DBZRQ1CT-ND','texas-instruments/ESD2CAN24DBZRQ1/16982262',255809,.87)
add('045101.5MRL','Littelfuse','F2579CT-ND','littelfuse-inc/045101-5MRL/700820')
add('SS36-E3/57T','Vishay')
add('SMBJ18A-E3/52','Vishay')
add('SMAJ30A-E3/61','Vishay')
add('EEE-FK1V470P','Panasonic Industry')
add('691137710002','Wurth Elektronik',stock=46145,price=.41)
add('691137710003','Wurth Elektronik',stock=5153,price=.66)
add('RT0805BRD07100KL','YAGEO','YAG1759CT-ND','yageo/RT0805BRD07100KL/5139207',60820,.10,'0.1%, 25ppm/C feedback resistor.',alt='ERA-6AEB1003V (0.1%, verify purchase suffix)')
add('RT0805BRD0713K7L','YAGEO','YAG4829CT-ND','yageo/RT0805BRD0713K7L/1075594',4402,.10,'0.1%, 25ppm/C feedback resistor.',alt='ERA-6AEB1372V; RG2012P-1372-B-T5')
add('RC2010FK-074K7L','YAGEO','13-RC2010FK-074K7LCT-ND','yageo/RC2010FK-074K7L/5921412',7566,.23,'4.7k, 1%, 0.75W; keep 2010 power rating.')
add('RC0805FR-07110KL','YAGEO','311-110KCRCT-ND','yageo/RC0805FR-07110KL/727560',5943,.10,alt='ERJ-6ENF1103V')
add('RC0805FR-07910KL','YAGEO','YAG3336CT-ND','yageo/RC0805FR-07910KL/5281196',59516,None,'Stock on DigiKey Italy; USD price pending.',alt='ERJ-6ENF9103V')
add('ERJ-6ENF1782V','Panasonic Industry','P17.8KCCT-ND','panasonic-industry/ERJ-6ENF1782V/6403',33381,.12,alt='RC0805FR-0717K8L; CRCW080517K8FKTA')
add('RC0805FR-077K15L','YAGEO','311-7.15KCRCT-ND','yageo/RC0805FR-077K15L/728110',48097,.10,alt='CR0805-FX-7151ELF')
add('ERJ-6ENF4871V','Panasonic Industry','P4.87KCCT-ND',stock=166982,note='Chosen over RC0805FR-074K87L, which had only78 reported units.',alt='CR0805-FX-4871ELF; RMCF0805FT4K87')
for mpn in ['RC0805FR-071KL','RC0805FR-0710KL','RC0805FR-07100KL','RC0805FR-0720KL','RC0805FR-0759KL','RC0805FR-074K7L','RC0805JR-070RL','RC1206FR-07120RL']:
 add(mpn,'YAGEO')
add('CL32B106KBJNNWE','Samsung Electro-Mechanics','1276-3388-1-ND','samsung-electro-mechanics/CL32B106KBJNNWE/3891474',149003,.62,'10uF,50V,X7R,1210; DigiKey US Spanish-language catalog observation.')
add('CL31A226KAHNNNE','Samsung Electro-Mechanics','1276-3047-1-ND',stock=426249,price=.48,note='22uF,25V,X5R,1206; verify effective capacitance under DC bias. Purchase limit exists but exceeds prototype quantities.',alt='TMK316BBJ226ML-T (20% tolerance requires capacitance recheck)')
add('CC0805KRX7R9BB104','YAGEO','311-1140-1-ND','yageo/CC0805KRX7R9BB104/302874',1921549,.11,'100nF,50V,X7R,0805; stock from DigiKey substitute table.',alt='C0805C104K5RACTU')
add('CC0805KRX7R9BB103','YAGEO','311-1136-1-ND','yageo/CC0805KRX7R9BB103/302870',360198,.11,'10nF,50V,X7R,0805; stock from DigiKey substitute table.',alt='C0805C103K5RACTU')
add('C0805C105K5RACTU','KEMET','399-C0805C105K5RACTUCT-ND','kemet/C0805C105K5RACTU/3317615',None,None,'1uF,50V,X7R,0805; 50V covers sensor-battery transients.')
add('TMK212AB7475KG-T','Taiyo Yuden','587-2990-1-ND','taiyo-yuden/TMK212AB7475KG-T/2714168',718393,.26,'4.7uF,25V,X7R,0805; stock from DigiKey US substitute table. New PN transition exists; verify lifecycle before volume ordering.',alt='CL21B475KAFNNNE')
add('CC0805JRNPO9BN102','YAGEO','311-1122-1-ND',stock=79318,note='1nF,50V,C0G,5%,0805; stock on DigiKey Poland substitute table.')
add('C0805C300J5GACTU','KEMET','399-C0805C300J5GACTUCT-ND','kemet/C0805C300J5GACTU/2209733',13252,None,'30pF,50V,C0G,5%,0805; stock on DigiKey Korea.')
for mpn in ['M20-9990245','M20-9990345','M20-9980345','M20-9980545','M7566-05']:
 add(mpn,'Harwin')
add('LTST-C170KGKT','Lite-On')
add('LTST-C170KRKT','Lite-On')

# Packaging and lifecycle review corrections.
CATALOG.pop('SS36-E3/57T') # SMC package, incompatible with this board's SMA pads.
CATALOG.pop('SMAJ30A-E3/61')
add('B360A-13-F','Diodes Incorporated','B360A-FDICT-ND','diodes-incorporated/B360A-13-F/724950',71743,.51,'SMA, 60V,3A. Manufacturer datasheet package verified.',alt='B360A-E3/61T (Vishay SMA); CDBA360-G')
add('SMAJ30A','Littelfuse','SMAJ30ALFCT-ND','littelfuse-inc/SMAJ30A/762294',104069,.50,'Unidirectional 30V TVS, SMA,48.4V clamp at8.3A. Order with the exact distributor SKU.',alt='SMAJ30A-13-F (Diodes Incorporated)')
add('SMBJ18A-E3/52','Vishay','SMBJ18A-E3/52GICT-ND','vishay-general-semiconductor-diodes-division/SMBJ18A-E3-52/2413378',38516,.51,'18V working standoff;29.2V clamp at20.5A.',alt='SMBJ18A (Bourns)')
add('EEE-FK1V470P','Panasonic Industry','PCE3842CT-ND','panasonic-industry/EEE-FK1V470P/766010',1183,.55,'47uF35V,6.3mm diameter,6.1mm max mounted height,240mA ripple at100kHz.')
add('M7566-05','Harwin','952-2201-ND','harwin-inc/M7566-05/3728166',7680,.37,'2.54mm,3A red gold-plated shunt. Buy13; normally fit only the required configuration shunts.')
add('M20-9990245','Harwin','952-2261-ND','harwin-inc/M20-9990245/3728225',66017,.12,'2-position,2.54mm,3A/gold,through-hole.')
add('M20-9990345','Harwin','952-2263-ND','harwin-inc/M20-9990345/3728227',75301,.15,'3-position,2.54mm,3A/gold,through-hole.')
add('M20-9980345','Harwin','952-2120-ND','harwin-inc/M20-9980345/3728084',14910,.29,'2x3,2.54mm,3A/gold,through-hole.')
add('M20-9980545','Harwin','952-2380-ND','harwin-inc/M20-9980545/2811108',11669,.45,'2x5,2.54mm,3A/gold,through-hole. Custom service connector.')
add('691137710002','Wurth Elektronik','732-10955-ND','w%C3%BCrth-elektronik/691137710002/6644051',46145,.41,'Exact 5.00mm pitch; do not silently replace with5.08mm.')
add('691137710003','Wurth Elektronik','732-10956-ND','w%C3%BCrth-elektronik/691137710003/6644052',5153,.66,'Exact 5.00mm pitch; do not silently replace with5.08mm.')
add('LTST-C170KGKT','Lite-On','160-1414-1-ND','lite-on-inc/LTST-C170KGKT/386777',498450,.19,'Green0805,typical Vf2V. Board current approximately1.3mA.')
add('LTST-C170KRKT','Lite-On','160-1415-1-ND','lite-on-inc/LTST-C170KRKT/386779',489805,.18,'Red0805,typical Vf2V. Board current approximately1.3mA.')
add('RC0805FR-071KL','YAGEO','311-1.00KCRCT-ND','yageo/RC0805FR-071KL/727444',894200,.10,'1k,1%,0.125W,0805.')
add('RC0805FR-0710KL','YAGEO','311-10.0KCRCT-ND','yageo/RC0805FR-0710KL/727535',2321007,.10,'10k,1%,0.125W,0805.')
add('RC0805FR-07100KL','YAGEO','311-100KCRCT-ND','yageo/RC0805FR-07100KL/727544',1152791,.11,'100k,1%,0.125W,0805.')
add('RC0805FR-074K7L','YAGEO','311-4.70KCRCT-ND','yageo/RC0805FR-074K7L/727929',564468,.10,'4.7k,1%,0.125W,0805.')
add('RC0805JR-070RL','YAGEO','311-0.0ARCT-ND','yageo/RC0805JR-070RL/728216',1733368,.10,'Zero-ohm0805 jumper; crystal characterization position.')
add('RC0805FR-0720KL','YAGEO','311-20.0KCRCT-ND','yageo/RC0805FR-0720KL/730667',27443,.10,'20k,1%,0.125W,0805.')
add('RC0805FR-0759KL','YAGEO','311-59.0KCRCT-ND','yageo/RC0805FR-0759KL/728045',29786,.10,'59k,1%,0.125W,0805.')
add('RC1206FR-07120RL','YAGEO','311-120FRCT-ND','yageo/RC1206FR-07120RL/728523',126570,.10,'120ohm,1%,0.25W,1206. Older duplicate catalog page reported zero stock; current main listing used.')
add('TPS1H200AQDGNRQ1','Texas Instruments','296-50416-1-ND','texas-instruments/TPS1H200AQDGNRQ1/9593381',25656,1.78,'4-40V,adjustable current limit,hardware latch-off. Replaces unavailable TPS1H100A; NOT footprint-compatible with it.')
add('RC0805FR-073K9L','YAGEO','311-3.90KCRCT-ND','yageo/RC0805FR-073K9L/727838',131203,.10,'3.9k,1%,0.125W,0805; nominal battery rail current limit513mA.')
add('CC0805KKX7R9BB105','YAGEO','311-1886-1-ND','yageo/CC0805KKX7R9BB105/5195292',112870,.32,'1uF,50V,X7R,10%,0805. Lower-cost stocked selection.',alt='C0805C105K5RACTU (KEMET)')
add('LM2901BIDR','Texas Instruments','296-LM2901BIDRCT-ND','texas-instruments/LM2901BIDR/21442011',3349,.29,'B-grade comparator required; older LM2901 variants have different error bounds.')
add('BAT46W-E3-18','Vishay','BAT46W-E3-18GICT-ND','vishay-general-semiconductor-diodes-division/BAT46W-E3-18/4826890',19931,.52,'100V reverse blocking, SOD123. Catalog showed$0.49-$0.52 by packaging; conservative price used. Do not substitute30V BAT54.')
add('045101.5MRL','Littelfuse','F2579CT-ND','littelfuse-inc/045101-5MRL/700820',7870,2.47,'1.5A fast NANO2 fuse; upstream fused distribution still required.')
add('RC0805FR-07910KL','YAGEO','YAG3336CT-ND','yageo/RC0805FR-07910KL/5281196',58915,.10,'910k,1%,0.125W,0805.',alt='ERJ-6ENF9103V')
add('C0805C300J5GACTU','KEMET','399-C0805C300J5GACTUCT-ND','kemet/C0805C300J5GACTU/2209733',9211,.33,'30pF,50V,C0G,5%,0805.')
CATALOG['CL31A226KAHNNNE']['digikey_url']='https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL31A226KAHNNNE/3888705'
CATALOG['CL31A226KAHNNNE']['availability_note']='22uF25VX5R1206. Manufacturer typical capacitance change is about-39% near5.18V; three parallel capacitors used on buck output.'
add('CC0805JRNPO9BN102','YAGEO','311-1122-1-ND','yageo/CC0805JRNPO9BN102/302856',105431,.15,'1nF,50V,C0G,5%,0805.')
add('QPC02SXGN-RC','Sullins Connector Solutions','S9337-ND','sullins-connector-solutions/QPC02SXGN-RC/2618262',2159145,.10,'2.54mm,3A,gold shunt; lower-cost stocked accessory. Buy13; fit only required settings.',alt='M7566-05 (Harwin, red)')

add('RT0805BRD07101KL','YAGEO','13-RT0805BRD07101KLCT-ND','yageo/RT0805BRD07101KL/17023410',4939,.10,'101k,0.1%,25ppm/C feedback resistor; centers regulated output at5.023V.')
add('CC0805KRX7R9BB333','YAGEO','311-1374-1-ND','yageo/CC0805KRX7R9BB333/2103112',24641,.14,'33nF,50V,X7R,10%,0805; battery switch latch timing. Direct US product listing checked2026-09-07.',alt='C0805C333K5RACTU; CC0805KPX7R9BB333 (verify package and timing tolerance)')
CATALOG['CC0805KRX7R9BB333']['unit_price_usd_qty10']=.078
CATALOG['RT0805BRD07101KL']['unit_price_usd_qty10']=.08

for mpn,price in {'AO4485':.95,'MMSZ12T1G':.102,'QPC02SXGN-RC':.029}.items():CATALOG[mpn]['unit_price_usd_qty10']=price
