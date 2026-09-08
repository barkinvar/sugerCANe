"""One-time D2 -> E model migration. Native CAD is updated separately."""
from pathlib import Path
import json,pprint,copy
R=Path(__file__).resolve().parents[1]
p=json.loads((R.parent/'rev_d2/hardware/design/circuit.json').read_text())['parts']
for ch,up,down in [(1,'11','14'),(2,'12','15'),(3,'13','27')]:
 z=ch*100;sheet=f'input{ch}'
 del p[f'JP{z+3}']
 p['U5']['pins'][up]=f'BIAS_UP{ch}_N';p['U5']['pins'][down]=f'BIAS_DOWN{ch}'
 p[f'D{z+2}']['pins']['2']=f'BIAS_SOURCE{ch}'
 p[f'R{z+10}'].update(value='1k',mpn='0805W8F1001T5E',note='Switched 3.3 V pull-up through reverse-blocking BAT46W; independent of sensor supply. About 3 mA maximum sink load.')
 p[f'R{z+10}']['pins']['2']=f'SIG{ch}'
 p[f'R{z+9}']['pins']={'1':f'SIG{ch}','2':f'BIAS_SINK{ch}'}
 p[f'R{z+9}']['note']='Electronically switched 10k pulldown; 0.09 W worst at 30 V, 1206 0.25 W.'
 for ref,kind,mpn,pins,note in [
  (f'Q{z+1}','PMOS3','AO3401A',{'1':f'BIAS_UP{ch}_N','2':'+3V3','3':f'BIAS_SOURCE{ch}'},'3.3 V bias source, active-low gate. BAT46W isolates positive field voltage.'),
  (f'Q{z+2}','NMOS3','BSS138BK,215',{'1':f'BIAS_DOWN{ch}','2':'GND','3':f'BIAS_SINK{ch}'},'60 V bias sink, active-high gate; 6.5 ohm max at VGS=2.5 V, 25 C.')]:
  p[ref]=dict(ref=ref,kind=kind,value=mpn.split(',')[0],pins=pins,sheet=sheet,footprint='FRC_Sensor_CAN:SOT-23',source_footprint='Package_TO_SOT_SMD:SOT-23',mpn=mpn,note=note)
 for offset,rail,net in [(11,'+3V3',f'BIAS_UP{ch}_N'),(12,'GND',f'BIAS_DOWN{ch}')]:
  ref=f'R{z+offset}';p[ref]=copy.deepcopy(p['R50']);p[ref].update(ref=ref,pins={'1':rail,'2':net},sheet=sheet,note='100k gate return holds bias OFF during reset, bootloader and unconfigured startup.')
p['R52']=copy.deepcopy(p['R3']);p['R52'].update(ref='R52',pins={'1':'+3V3','2':'GND'},sheet='input1',note='10k logic-rail bleed bounds reverse-diode leakage with board power removed; not galvanic isolation.')
p['U5']['note']='Three comparator inputs PA0/1/2. PA5/6/7 active-low pull-up gates; PB0/1/4 active-high pulldown gates. CAN service config; no software sensor-power control.'
text='"""Rev E explicit model: electronically selected input bias, protected digital inputs."""\nfrom pathlib import Path\nimport json\nROOT=Path(__file__).resolve().parents[2]\nPARTS='+pprint.pformat(p,sort_dicts=False,width=105)+'\n\ndef export():\n    (ROOT/"hardware/design/circuit.json").write_text(json.dumps({"parts":PARTS},indent=2)+"\\n")\n\nif __name__=="__main__":export()\n'
(R/'hardware/design/circuit.py').write_text(text)
(R/'hardware/design/circuit.json').write_text(json.dumps({'parts':p},indent=2)+'\n')
c=json.loads((R/'bom/catalog_china.json').read_text())
for mpn,man,code,stock,moq,tiers in [('AO3401A','Alpha & Omega Semiconductor','C15127',14725,5,[[5,.095],[50,.0764],[150,.0668],[500,.0589]]),('BSS138BK,215','Nexperia','C282529',77720,10,[[10,.0674],[100,.0533],[300,.0463],[3000,.0401]])]:
 c[mpn]=dict(mpn=mpn,manufacturer=man,supplier='LCSC',supplier_part=code,url=f'https://www.lcsc.com/product-detail/{code}.html',lcsc=code,stock_observed=stock,observed_date='2026-09-08',moq=moq,multiple=moq,tiers=tiers,digikey_sku='',digikey_url='',factory_stock_status='LCSC listing observed; JLCPCB allocation/classification unverified')
(R/'bom/catalog_china.json').write_text(json.dumps(c,indent=2)+'\n')
print(len(p),'modeled parts')
