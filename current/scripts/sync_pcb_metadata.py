"""Update reviewed purchasing fields without moving copper or footprints."""
from pathlib import Path
import json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
parts=json.loads((ROOT/'hardware/design/circuit.json').read_text())['parts']
path=ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'
b=p.LoadBoard(str(path))
footprints={f.GetReference():f for f in b.GetFootprints()}
for ref,c in parts.items():
    f=footprints.get(ref)
    assert f, ref
    f.SetValue(c['value'])
    for key,value in [('MPN',c.get('mpn','')),('Notes',c.get('note','')),
                      ('Voltage',c.get('voltage','')),('Tolerance',c.get('tolerance',''))]:
        f.SetField(key,value)
        f.GetField(key).SetVisible(False)
p.SaveBoard(str(path),b)
print(f'Synchronized metadata for {len(parts)} parts; copper unchanged.')
