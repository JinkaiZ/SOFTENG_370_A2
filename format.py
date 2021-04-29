#!/usr/bin/env python

import logging
import os
import bits
import disktools
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

NUM_BLOCKS = 16
BLOCK_SIZE = 64
DISK_NAME = 'my-disk'

# Fix metadata locations in for root directory block
BITMAP_START = 0
BITMAP_FINISH = 2


# Fix metadata locations in for each block
MODE_START = 2
MODE_FINISH = 4
UID_START = 4
UID_FINISH = 8
GID_START = 8
GID_FINISH = 10
NLINK_START = 10
NLINK_FINISH = 11
CTIME_START = 11
CTIME_FINISH = 15
MTIME_START = 15
MTIME_FINISH = 19
ATIME_START = 19
ATIME_FINISH = 23
SIZE_START = 23
SIZE_FINISH = 25
LOCATION_START = 25
LOCATION_FINISH = 28
NAME_START = 28
NAME_FINISH = 44





class Format:

    def initial_bitmap(self):
        self.update_free_block_bitmap(Format)

    def update_free_block_bitmap(self):
        # initialise the bitmap int value to 0
        bitmap = 0
        # counter for count the blocks
        count = 0
        for i in range(NUM_BLOCKS):
            # read each block in the disk
            block = disktools.read_block(i)

        # set the value to 0 for the non-free block in bit map
            if disktools.bytes_to_int(block) != 0:
                bitmap = bits.clearBit(bitmap, count)
                count += 1
            else:
                bitmap = bits.setBit(bitmap, count)
                count += 1

        # write the bitmap value at the first two bytes at block 0
        block = disktools.read_block(0)
        block[BITMAP_START:BITMAP_FINISH] = disktools.int_to_bytes(bitmap, 2)
        disktools.write_block(0, block)

        return bitmap

    # return the first int of the
    def get_free_block(self, num_of_blocks):
        bit_array = []
        free_block = []
        bitmap_int = self.update_free_block_bitmap(Format)
        bitmap_bin = bin(bitmap_int)
        for b in bitmap_bin[2:]:
            bit_array.append(int(b))

        bit_array = reversed(bit_array)

        for idx, val in enumerate(bit_array):
            if val == 1:
                free_block.append(idx)

        return free_block[0:num_of_blocks]






    def set_inode(self, name, mode, ctime, mtime, atime, nlink, uid, gid, size):
        block = disktools.read_block(0)
        block[MODE_START:MODE_FINISH] = disktools.int_to_bytes(mode, 2)
        block[UID_START:UID_FINISH] = disktools.int_to_bytes(uid, 2)
        block[GID_START:GID_FINISH] = disktools.int_to_bytes(gid, 2)
        block[NLINK_START:NLINK_FINISH] = disktools.int_to_bytes(nlink, 1)
        block[SIZE_START:SIZE_FINISH] = disktools.int_to_bytes(size, 2)
        block[CTIME_START:CTIME_FINISH] = disktools.int_to_bytes(int(ctime), 4)
        block[MTIME_START:MTIME_FINISH] = disktools.int_to_bytes(int(mtime), 4)
        block[ATIME_START:ATIME_FINISH] = disktools.int_to_bytes(int(atime), 4)
        block[NAME_START:NAME_FINISH] = name.encode()

        return block


if __name__ == '__main__':
    # Format.initial_bitmap(Format)
    # Format.update_free_block_bitmap(Format)

    a = Format.get_free_block(Format, 3)
    print(a)

    # block = disktools.read_block(1)
    # print(len(block))