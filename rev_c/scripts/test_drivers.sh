#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source tools/env.sh
CANDI_JDK="${CANDI_JDK:-$CANDI_TOOLS_ROOT/java-jdk/jdk-17.0.20.1+1}"
mkdir -p reports/driver/classes
"$CANDI_JDK/bin/javac" -Xlint:all -Werror -cp 'reports/driver/deps/*' -d reports/driver/classes \
 examples/java/src/main/java/frc/robot/sensors/*.java examples/java/src/test/java/frc/robot/sensors/*.java
"$CANDI_JDK/bin/java" -cp 'reports/driver/classes:reports/driver/deps/*' frc.robot.sensors.SensorCanLiteTest
python -m unittest discover -s host -p 'test_*.py' -v
export LD_LIBRARY_PATH="${CANDI_TOOLS_ROOT}/native-gcc/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
host-g++ -std=c++17 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined \
 -Iexamples/cpp/include examples/cpp/tests/test_sensor_can.cpp -o reports/driver/test_sensor_can_cpp
reports/driver/test_sensor_can_cpp
host-g++ -std=c++17 -Wall -Wextra -Werror -Iexamples/cpp/include -Ireports/driver/cpp-deps \
 -c examples/cpp/ReadSensorExample.cpp -o reports/driver/read_example.o
