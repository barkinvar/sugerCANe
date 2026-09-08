"""Export a two-layer routing model; preserve the native four-layer PCB.

Use KiCad's DSN writer so numeric pin identifiers retain Specctra syntax.
The two inner copper layers are reserved for ground planes.
"""
from pathlib import Path
import pcbnew as p
R = Path(__file__).resolve().parents[1]
b = p.LoadBoard(str(R / 'hardware/prerouted.kicad_pcb'))
assert b.GetCopperLayerCount() == 4
b.GetDesignSettings().SetCopperLayerCount(2)
assert b.GetCopperLayerCount() == 2
assert p.ExportSpecctraDSN(b, str(R / 'hardware/design/outer_layers.dsn'))
print('Exported outer-layer routing model; native four-layer PCB preserved.')
