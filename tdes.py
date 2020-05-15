# Taint-Driven Embedded Software Fuzzer

import configparser
import os
import string
import subprocess
import sys
import time

from collections import deque
from datetime import datetime as dt
from mutate import File
from mutate import Mutate
from os.path import abspath
from shutil import copyfile

# Update me!
plog_reader_path = '/home/mksavic/git/tdes/avatar2/targets/src/avatar-panda/panda/scripts'
sys.path.append(plog_reader_path)
from plog_reader import PLogReader

class TDES:
    def __init__(self, device):
        """
        Args:
            device: (str) The name of the device.
        """
        config = configparser.ConfigParser()
        config.read('config')

        if device in config:
            self.record_path = config[device]['record_path']
            self.input_dir = config[device]['input_dir']
            self.plog_dir = config[device]['plog_dir']
            self.mmio_start_addr = config[device]['mmio_start_addr']
            self.mmio_end_addr = config[device]['mmio_end_addr']
            self.exit_addr = config[device]['exit_addr']
            self.label_offset = int(config[device]['label_offset'])
        else:
            raise NotImplementedError

        self.pcs = []
        self.labels = []
        self.blocks = set()

    def record(self, filename='initial'):
        """Calls some pre-specified script to create a PANDA recording.

        Args:
            filename: (str) The name of the PANDA recording script.
        """
        record_begin = time.time()

        try:
            cmd = '{} {}/{} > /dev/null 2>&1'.format(self.record_path, self.input_dir, filename)
            subprocess.call(cmd, shell=True)
        except IOError:
            pass

        record_end = time.time()
        print('[DEBUG] {}: record() took {} seconds to complete'.format(dt.now(), record_end - record_begin))

    def replay(self, filename='initial'):
        """Performs a PANDA replay which creates the necessary PANDA log.

        Args:
            filename: (str) The name of the PANDA log.
        """
        replay_begin = time.time()

        cmd = ('/home/mksavic/git/tdes/avatar2/targets/build/panda/panda/arm-softmmu/qemu-system-arm \\'
               '-M configurable \\'
               '-kernel /tmp/avatar/conf.json \\'
               '-replay /tmp/avatar/panda_record \\'
               '-panda io_taint::start_addr={},end_addr={},exit_addr={} \\'
               '-panda tainted_branch \\'
               '-pandalog {} \\'
               '-d taint_ops > /dev/null 2>&1'.format(self.mmio_start_addr, self.mmio_end_addr, self.exit_addr, self.plog_dir + '/' + filename))
        subprocess.call(cmd, shell=True)

        replay_end = time.time()
        print('[DEBUG] {}: replay() took {} seconds to complete'.format(dt.now(), replay_end - replay_begin))

    def explore(self, input_filename='initial', plog_filename='initial'):
        """Reviews the given PANDA log to see if new blocks were encountered.
           Mutates the given input file if new (pc, label) pairs were encountered.

        Args:
            input_filename: The name of the input file.
            plog_filename: The name of the PANDA log.
        """
        # FIXME: Sometimes the PANDA log is not written to. Not sure why.
        plog = self.plog_dir + '/' + plog_filename
        if not os.stat(plog).st_size:
            return

        new_blocks = set()
        d = deque()
        with PLogReader(plog) as plr:
            for i, m in enumerate(plr):
                # See if there is a taint_query attribute.
                if m.tainted_branch.taint_query:
                    labels = m.tainted_branch.taint_query[0].unique_label_set.label
                    if len(labels) == 1: # FIXME: Multi-label mutations not yet implemented.
                        if (labels[0] >= self.label_offset) and (labels[0] not in self.labels):
                            print('[DEBUG] {}: new (pc, label) pair (0x{:02x}, {})'.format(dt.now(), m.pc, labels[0]))

                            # Add the pc and label to the list of explored branches.
                            self.pcs.append(m.pc)
                            self.labels.append(labels[0])

                            # Explore this branch.
                            offset = labels[0] - self.label_offset - 1
                            input_file = self.input_dir + '/' + input_filename
                            mu = Mutate(offset, input_file, self.input_dir, self.plog_dir)

                            # Add new inputs to the queue.
                            d.appendleft(mu.get_files())

                # See if there is an io_taint attribute.
                if m.io_taint:
                    new_blocks.add('0x{:02x}'.format(m.io_taint.tb_pc))

        # Determine if any new blocks were encountered.
        if bool(new_blocks.difference(self.blocks)):
            print('[DEBUG] {}: new blocks encountered from previous input {}'.format(dt.now(), new_blocks.difference(self.blocks)))
            self.blocks.update(new_blocks)

        # Explore!
        while d:
            files = d.popleft()
            for f in files:
                with open(f.input_file, 'rb') as g:
                    data = g.read()
                    print('[DEBUG] {}: trying input... {}'.format(dt.now(), data))

                input_filename = os.path.basename(f.input_file)
                plog_filename = os.path.basename(f.plog_file)

                self.record(input_filename)
                self.replay(plog_filename)
                self.explore(input_filename, plog_filename)


if __name__ == '__main__':
    program_begin = time.time()
    print('[DEBUG] {}: Program start.'.format(dt.now()))

    # Setup TDES.
    if len(sys.argv) == 1:
        exit('[ERROR] Please specify device name on the command line.')
    tdes = TDES(sys.argv[1])

    # Perform the initial recording.
    tdes.record()

    # Perform the initial replay.
    tdes.replay()

    # Start exploring branches.
    tdes.explore()

    program_end = time.time()
    print('[DEBUG] {}: Program took {} seconds to complete.'.format(dt.now(), program_end - program_begin))
