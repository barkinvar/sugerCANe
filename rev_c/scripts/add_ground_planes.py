"""Refill the two saved ground planes without changing their boundaries."""
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];f=R/'hardware/FRC_Sensor_CAN.kicad_pcb';b=p.LoadBoard(str(f))
assert len([z for z in b.Zones() if not z.GetIsRuleArea()])==2
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
