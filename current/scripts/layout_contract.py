"""Explicit mechanical/assembly intent shared by independent export checks."""
import json
from pathlib import Path

CONTRACT = json.loads((Path(__file__).resolve().parents[1] /
                       'hardware/design/layout_contract.json').read_text())
WIDTH = CONTRACT['width_mm']
HEIGHT = CONTRACT['height_mm']
RADIUS = CONTRACT['corner_radius_mm']
BOTTOM_REFERENCES = set(CONTRACT['bottom_references'])
