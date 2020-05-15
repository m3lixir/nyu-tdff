#!/usr/bin/env python3

import os
import tempfile

from collections import deque

class File:
    pass

class Mutate:
    def __init__(self, offset, input_file, input_dir, plog_dir):
        """
        Args:
            offset: (int) The offset in the input file to be mutated.
            input_file: (str) The absolute path to the input file.
            input_dir: (str) The absolute path to /inputs.
            plog_dir: (str) The absolute path to /plogs.
        """
        self.offset = offset
        self.input_file = input_file
        self.input_dir = input_dir
        self.plog_dir = plog_dir

    def bit_flip(self, byte):
        """Performs a series of bit flips on the input byte.

        Args:
            byte: (bytes) The byte to perform the series of bit flips on.

        Returns:
            A list (bytes) containing the resulting new bytes.
        """
        result = []

        for j in range(1, 9):
            bits = 2**j - 1
            for i in range(8 - j + 1):
                result.append((byte ^ (bits << i)) & 0xFF)

        return result

    def add_subtract(self, byte):
        """Performs a series of additions/subtractions on the input byte.

        Args:
            byte: (bytes) The byte to perform the series of additions/subtractions on.

        Returns:
            A list (bytes) containing the resulting new bytes.
        """
        result = []

        for i in range(-35, 36):
            result.append(((byte + i) % 256) & 0xFF)

        return result

    def interesting_bytes(self, byte):
        """Replaces the input byte with common/interesting bytes.

        Args:
            byte: (bytes) The byte to replace.

        Returns:
            A list (bytes) containing the resulting new bytes.
        """
        # 0, 1, '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 255
        result = [0x00, 0x01, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
                  0x38, 0x39, 0xFF]

        return result

    def make_file(self, buf, new_byte):
        """Modifies buf with new_byte, and creates a new File object.

        Args:
            buf: (list (bytes)) The original contents of the input file.
            new_byte: (bytes) The new byte to write to buf.

        Returns:
            The resulting new File object, containing the absolute paths of the
            new input and plog files.
        """
        # Write new_byte to buf.
        buf[self.offset] = new_byte

        # Create and write to new input file.
        fd, input_file = tempfile.mkstemp(dir=self.input_dir)  # FIXME: Prefix?
        with open(input_file, 'wb') as f:
            f.write(bytes(buf))
        os.close(fd)

        # Create new plog file.
        fd, plog_file = tempfile.mkstemp(dir=self.plog_dir)  # FIXME: Prefix?
        os.close(fd)

        # Create File object
        x = File()
        x.input_file = input_file
        x.plog_file = plog_file

        return x

    def fuzz(self):
        """Creates new input/plog files by mutating the original input file.

        Returns:
            A list (File) containing the resulting new input files.
        """
        # Copy contents of input file into buf.
        with open(self.input_file, 'rb') as f:
            buf = list(f.read())

        # The byte to fuzz.
        byte = buf[self.offset]

        # Our "queue".
        new_bytes = set()

        # Perform bit flips.
        new_bytes.update(self.bit_flip(byte))

        # Perform additions/subtractions.
        new_bytes.update(self.add_subtract(byte))

        # Perform interesting bytes.
        new_bytes.update(self.interesting_bytes(byte))

        # Create new input files.
        files = deque()
        for new_byte in new_bytes:
            x = self.make_file(buf, new_byte)
            files.append(x)

        return files

    def get_files(self):
        """Wrapper for fuzz().
        """
        return self.fuzz()
