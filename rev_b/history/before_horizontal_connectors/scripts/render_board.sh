#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
mkdir -p output/review
kicad-cli pcb render --width 1600 --height 1700 --quality high --background opaque --floor \
  --rotate '-25,0,25' --zoom 0.72 -o output/review/board_3d_final.png hardware/FRC_Sensor_CAN.kicad_pcb
