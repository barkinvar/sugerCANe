#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
board=hardware/FRC_Sensor_CAN.kicad_pcb
mkdir -p output/fabrication output/assembly output/mechanical
kicad-cli pcb drc --exit-code-violations --severity-all --format json -o reports/drc/final.json "$board"
kicad-cli sch erc --exit-code-violations --severity-all --format json -o reports/erc/final.json hardware/FRC_Sensor_CAN.kicad_sch
kicad-cli sch export netlist --format kicadxml -o hardware/design/schematic.net.xml hardware/FRC_Sensor_CAN.kicad_sch
kicad-python scripts/check_design_parity.py
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask --check-zones -o output/fabrication/ "$board"
kicad-cli pcb export drill --format excellon --excellon-units mm --excellon-zeros-format decimal --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path output/fabrication/drill_report.txt -o output/fabrication/ "$board"
kicad-cli pcb export pos --format csv --units mm --side front --exclude-dnp -o output/assembly/positions_all_top.csv "$board"
kicad-cli pcb export pos --format csv --units mm --side front --smd-only --exclude-dnp -o output/assembly/positions_smd_top.csv "$board"
python scripts/export_assembly_drawing.py
kicad-cli pcb export pdf --mode-single --layers B.Silkscreen,Edge.Cuts --mirror --scale 2 --black-and-white -o output/assembly/bottom_markings.pdf "$board"
kicad-cli pcb export svg --mode-single --layers F.Cu,F.Mask,F.Silkscreen,Edge.Cuts --fit-page-to-board -o output/assembly/top_copper.svg "$board"
kicad-cli pcb export svg --mode-single --layers B.Cu,B.Mask,B.Silkscreen,Edge.Cuts --fit-page-to-board --mirror -o output/assembly/bottom_copper.svg "$board"
kicad-cli sch export pdf -o output/assembly/schematic.pdf hardware/FRC_Sensor_CAN.kicad_sch
ibom --no-browser --dest-dir ../output/assembly --name-format interactive_bom --include-tracks --include-nets --highlight-pin1 all --layer-view F --blacklist 'TP*,H*' --extra-data-file hardware/design/schematic.net.xml --extra-fields MPN,Notes "$board"
kicad-cli pcb export step --force --no-dnp --user-origin 0x0mm -o output/mechanical/FRC_Sensor_CAN.step "$board"
