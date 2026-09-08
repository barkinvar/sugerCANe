#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
source tools/env.sh
export LD_LIBRARY_PATH="${CANDI_TOOLS_ROOT}/native-gcc/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
make -C firmware > reports/firmware-build.log 2>&1
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/include firmware/tests/test_core.c firmware/src/sensor_core.c firmware/src/input_mode.c -o firmware/build/test_core
firmware/build/test_core > reports/firmware-tests.log
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/include firmware/tests/test_input_mode.c firmware/src/input_mode.c -o firmware/build/test_input_mode
firmware/build/test_input_mode >> reports/firmware-tests.log
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/tests/fake_board -Ifirmware/include -Dmain=firmware_main -c firmware/src/main.c -o firmware/build/host_application.o
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -Ifirmware/tests/fake_board -Ifirmware/include firmware/tests/test_application.c firmware/src/sensor_core.c firmware/src/input_mode.c firmware/src/service.c firmware/build/host_application.o -o firmware/build/test_application
for scenario in runtime_modes float maintenance normal unconfigured clock_failure can_failure disable config bad_commands busy uart old_uart overflow stall rail12_fault rail5_fault rail_chatter; do
 firmware/build/test_application "$scenario" >> reports/firmware-tests.log
done
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -Wno-clobbered -fsanitize=address,undefined -Ifirmware/include firmware/tests/service_sim.c firmware/src/service.c firmware/src/sensor_core.c firmware/src/input_mode.c -o firmware/build/test_service
firmware/build/test_service >> reports/firmware-tests.log
host-gcc -std=c11 -O1 -g -Wall -Wextra -Werror -shared -fPIC -DSC_SIM_LIBRARY -Ifirmware/include firmware/tests/service_sim.c firmware/src/service.c firmware/src/sensor_core.c firmware/src/input_mode.c -o firmware/build/service_sim.so
python -m unittest discover -s host -p 'test_service.py' -v >> reports/firmware-tests.log 2>&1
python firmware/tests/test_arm_registers.py >> reports/firmware-tests.log
python scripts/check_firmware_images.py >> reports/firmware-tests.log
tclsh firmware/tests/test_factory_script.tcl >> reports/firmware-tests.log
cat reports/firmware-tests.log
