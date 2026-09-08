# Invoke via OpenOCD with interface/stlink.cfg and target/stm32f0x.cfg.
# Run from rev_d2. Existing 0.4.0 boards require this one-time SWD migration.
# Never mass erase: configuration pages must remain intact. No RDP changes.
init
reset halt
flash probe 0
# STM32F042: 32 KiB; WRP granularity four 1 KiB pages. Refuse another flash size.
set flash_kib [mrh 0x1ffff7cc]
if {$flash_kib != 32} { error "Expected STM32F042 32 KiB flash; inspect device before programming" }
set device [expr {[mrw 0x40015800] & 0xfff}]
if {$device != 0x445} { error "Expected STM32F04x device ID 0x445" }
# An already protected bootloader is verified; it must not be erased for normal updates.
if {[expr {[mrw 0x40022020] & 255}] != 255} {
    error "Bootloader protection already enabled; use CAN application update or reviewed SWD recovery"
}
flash write_image erase firmware/build/factory.hex
verify_image firmware/build/factory.hex
# OpenOCD indexes 4 KiB PROTECTION BLOCKS here, not 1 KiB erase pages.
flash protect 0 0 1 on
reset halt
# Option-byte reload needs a power cycle on this target. Check the option bytes now.
if {[mrh 0x1ffff808] != 0x03fc} { error "Bootloader write-protection option verification failed" }
echo "Factory image verified and boot protection options set. Power cycle, then verify boot_protected via CAN."
shutdown
