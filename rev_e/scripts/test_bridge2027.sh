#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
: "${CANDI_JDK25:?Set CANDI_JDK25 to a JDK 25 installation}"
python tools/fetch_driver_dependencies.py tools/bridge2027_dependencies.json
mkdir -p reports/driver/classes2027
"$CANDI_JDK25/bin/javac" -Xlint:all -Werror -cp 'reports/driver/deps2027/*' -d reports/driver/classes2027 \
 examples/bridge/src/frc/robot/maintenance/ServiceBridge.java examples/bridge/wpilib2027/frc/robot/maintenance/Wpilib2027.java
printf '%s\n' 'PASS: WPILib 2027.0.0-alpha-7 CANPort bridge compiled with JDK 25; controller test pending'
