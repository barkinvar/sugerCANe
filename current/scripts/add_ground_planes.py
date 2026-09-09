"""Create/refill four ground pours; inner copper contains no signal routing."""
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];f=R/'hardware/FRC_Sensor_CAN.kicad_pcb';b=p.LoadBoard(str(f))
assert b.GetCopperLayerCount()==4
existing={z.GetLayer():z for z in b.Zones() if not z.GetIsRuleArea()}
for layer in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu):
 if layer in existing:
  assert existing[layer].GetNetname()=='GND';continue
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.GetNetsByName()['GND']);z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2));z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL if layer in (p.In1_Cu,p.In2_Cu) else p.ZONE_CONNECTION_THERMAL)
 poly=z.Outline();poly.NewOutline()
 for x,y in ((.3,.3),(51.7,.3),(51.7,63.7),(.3,63.7)):poly.Append(p.VECTOR2I(p.FromMM(x),p.FromMM(y)))
 b.Add(z)
assert len([z for z in b.Zones() if not z.GetIsRuleArea()])==4
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
print('Filled F.Cu / In1.Cu / In2.Cu / B.Cu ground zones.')
