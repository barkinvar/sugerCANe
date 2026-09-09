# Firmware vendor subset

This directory retains the unmodified STM32F042 device headers, GCC startup file and Cortex-M0 CMSIS headers actually used by this build. Other MCU families, DSP examples and unused compiler/startup variants were removed from the current tree to reduce clutter. Compiler dependency files and a clean rebuild verify the retained set.

The files were inherited from the project's CMSIS snapshot in commit 9ccb4b7. Original copyright/license notices remain in each file and in this directory; repository copies of the [Arm license](../../licenses/Arm_CMSIS_license.txt) and [ST license](../../licenses/ST_CMSIS_device_license.md) are also retained. The original full snapshots remain available in the historical source tree and release archives.
