#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p output/review
kicad-cli pcb render --width 1600 --height 1700 --quality high --background opaque --floor \
  --rotate '-25,0,25' --zoom 0.72 -o output/review/board_3d_final.png hardware/FRC_Sensor_CAN.kicad_pcb

kicad-cli pcb render --side top --width 1400 --height 1700 --quality high --background opaque --zoom 0.8 -o output/review/board_top.png hardware/FRC_Sensor_CAN.kicad_pcb
kicad-cli pcb render --side bottom --width 1400 --height 1700 --quality high --background opaque --zoom 0.8 -o output/review/board_bottom.png hardware/FRC_Sensor_CAN.kicad_pcb

# Lower viewpoint exposes horizontal wire entries and release buttons.
kicad-cli pcb render --width 1600 --height 1200 --quality high --background opaque --floor \
  --rotate '-55,0,25' --zoom 0.65 -o output/review/board_connectors.png hardware/FRC_Sensor_CAN.kicad_pcb
