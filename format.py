#!/usr/bin/env python

import logging
import os
import bits
import disktools
import small
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

BLOCK_SIZE = 64

class Format():

    def get_free_block_bitmap(self):
        # initialise the bitmap int value to 0
        bitmap = 0
        # counter for count the blocks
        count = 0
        file = open("my-disk", "rb")
        file_content = file.read()
        # read each 64 bytes as a block
        for i in range(0,1023,64):
            block = file_content[i:i+64]
            # If the first byte of a block is empty then the block is empty
            # The first data will always write into the first byte for each block
            if block[0] != 0:
                bitmap = bits.clearBit(bitmap, count)
                j+=1
            else:
                bitmap = bits.setBit(bitmap, count)
                j+=1

        print(bitmap)
        # write the bitmap value back to disk
        disktools.write_block(0, disktools.int_to_bytes(bitmap, 2))
        return 0

    def set_root_dir_inode(self):
        files['/'] = dict(
            st_mode=(S_IFDIR | 0o755),
            st_ctime=555.555,
            st_mtime=444.444,
            st_atime=3333.333,
            st_nlink=2)
        print(files)

if __name__ == '__main__':
    Format.set_root_dir_inode(Format())

