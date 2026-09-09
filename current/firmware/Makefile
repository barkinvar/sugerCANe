CROSS ?= arm-none-eabi-
CC = $(CROSS)gcc
SIZE = $(CROSS)size
OBJCOPY = $(CROSS)objcopy
OUT = build
CPU = -mcpu=cortex-m0 -mthumb
INC = -Iinclude -Ithird_party/cmsis_device_f0/Include -Ithird_party/CMSIS_5/CMSIS/Core/Include
CFLAGS = $(CPU) $(INC) -DSTM32F042x6 -DHSE_VALUE=8000000U -Os -g3 -std=c11 -ffunction-sections -fdata-sections -fno-common -fstack-usage -Wall -Wextra -Werror -MMD -MP
LDFLAGS = -nostartfiles $(CPU) -Tstm32f042k6.ld --specs=nano.specs --specs=nosys.specs -Wl,--gc-sections,-Map=$(OUT)/sensor_can.map -Wl,--print-memory-usage
SOURCES = src/power.c src/main.c src/board.c src/status.c src/sensor_core.c src/input_mode.c src/service.c src/board_service.c
OBJECTS = $(SOURCES:src/%.c=$(OUT)/%.o) $(OUT)/startup.o
all: $(OUT)/sensor_can.elf $(OUT)/sensor_can.bin $(OUT)/sensor_can.hex $(OUT)/bootloader.bin $(OUT)/factory.hex $(OUT)/application.sc12
$(OUT):
	mkdir -p $(OUT)
$(OUT)/%.o: src/%.c | $(OUT)
	$(CC) $(CFLAGS) -DSC_APPLICATION -c $< -o $@
$(OUT)/startup.o: third_party/cmsis_device_f0/Source/Templates/gcc/startup_stm32f042x6.s | $(OUT)
	$(CC) $(CPU) -x assembler-with-cpp -c $< -o $@
$(OUT)/sensor_can.elf: $(OBJECTS) stm32f042k6.ld
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SIZE) $@
$(OUT)/sensor_can.bin: $(OUT)/sensor_can.elf
	$(OBJCOPY) -O binary $< $@
$(OUT)/sensor_can.hex: $(OUT)/sensor_can.elf
	$(OBJCOPY) -O ihex $< $@
clean:
	rm -rf $(OUT)
-include $(OBJECTS:.o=.d)
.PHONY: all clean

BOOT_SOURCES = src/boot_main.c src/board.c src/status.c src/sensor_core.c src/input_mode.c src/service.c src/board_service.c
BOOT_OBJECTS = $(BOOT_SOURCES:src/%.c=$(OUT)/boot_%.o) $(OUT)/startup.o
$(OUT)/boot_%.o: src/%.c | $(OUT)
	$(CC) $(CFLAGS) -c $< -o $@
$(OUT)/bootloader.elf: $(BOOT_OBJECTS) bootloader.ld
	$(CC) $(BOOT_OBJECTS) -nostartfiles $(CPU) -Tbootloader.ld --specs=nano.specs --specs=nosys.specs -Wl,--gc-sections,-Map=$(OUT)/bootloader.map -Wl,--print-memory-usage -o $@
	$(SIZE) $@
$(OUT)/bootloader.bin: $(OUT)/bootloader.elf
	$(OBJCOPY) -O binary $< $@
$(OUT)/factory.hex $(OUT)/application.sc12 &: $(OUT)/bootloader.bin $(OUT)/sensor_can.bin ../host/firmware_image.py
	python ../host/firmware_image.py --build $(OUT)
-include $(BOOT_OBJECTS:.o=.d)
