#!/usr/bin/env python3
import sys

from avatar2 import *
from os.path import abspath
from serial import Serial
from time import sleep


def main():
#    import logging
#    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # Configure the location of various files.
    ############################################################################
    firmware = abspath('examples/vuzzer/firmware/BUILD/firmware.bin')
    openocd_config = abspath('examples/vuzzer/record/nucleo-f207zg.cfg')
    panda_path = '/home/mksavic/git/tdes/avatar2/targets/build/panda/panda/arm-softmmu/qemu-system-arm'
    ############################################################################

    # Initiate the avatar-object.
    ############################################################################
    avatar = Avatar(arch=ARM_CORTEX_M3, output_directory='/tmp/avatar')
    ############################################################################

    # Create the target-objects.
    ############################################################################
    nucleo = avatar.add_target(OpenOCDTarget, openocd_script=openocd_config,
            gdb_executable='arm-none-eabi-gdb')
    panda = avatar.add_target(PandaTarget, executable=panda_path,
            gdb_executable='arm-none-eabi-gdb', gdb_port=1236)
    ############################################################################

    # Define the various memory ranges and store references to them.
    ############################################################################
    rom  = avatar.add_memory_range(0x08000000, 0x1000000, file=firmware)
    ram  = avatar.add_memory_range(0x20000000, 0x20000)
    mmio = avatar.add_memory_range(0x40000000, 0x1000000,
                                   forwarded=True, forwarded_to=nucleo)
    ############################################################################

    # Initialize the targets.
    ############################################################################
    avatar.init_targets()
    ############################################################################

    # 1) Load the plugin.
    ############################################################################
    avatar.load_plugin('orchestrator')
    ############################################################################

    # 2) Specify the first target of the analysis.
    ############################################################################
    avatar.start_target = nucleo
    ############################################################################

    # 3) Configure transitions.
    #    Here, only one transition is defined. Note that 'stop=True' forces
    #    the orchestration to stop once the transition has occurred.
    ############################################################################
    avatar.add_transition(0x80002c8, nucleo, panda, synced_ranges=[ram],
                          stop=True)
    ############################################################################

    # 4) Start the orchestration!
    ############################################################################
    avatar.start_orchestration()
    print("State transfer finished, emulator $pc is: 0x%x" % panda.regs.pc)
    ############################################################################

    # 5) Begin PANDA recording.
    ############################################################################
    panda.begin_record('panda_record')
    avatar.resume_orchestration(blocking=False)
    ############################################################################

    # 6) Provide input.
    ############################################################################
    with open(sys.argv[1], 'rb') as file:
        data = file.read()

    ser = Serial('/dev/ttyACM0')
    for d in data:
        ser.write(bytes([d]))
        sleep(1.5)
    ############################################################################

    # Let this example run for a bit before shutting down avatar cleanly.
    ############################################################################
    sleep(5)
    panda.stop()
    panda.end_record()
    avatar.stop_orchestration()
    sleep(1)
    ############################################################################


if __name__ == '__main__':
    main()
