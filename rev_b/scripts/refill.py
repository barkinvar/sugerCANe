from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];f=R/'hardware/finishing.kicad_pcb'
b=p.LoadBoard(str(f));b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(f),b)
