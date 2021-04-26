#!/usr/bin/env python

import logging
import os
import disktools
import memory
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

BLOCK_SIZE = 64

class Format():

    def get_disk_info(self):
        file = open("my-disk", "rb")
        # block = slice(0, 1023, 64)
        file_content = file.read()
        # get the total number of bytes of the disk.
        total_num_bytes = len(file_content)
        # get the total number of blocks of the disk.
        total_num_blocks = total_num_bytes / BLOCK_SIZE
        #super_block = file_content[0:3]
        mode = file_content[0:2]
        print(disktools.bytes_to_int(mode))
        #F disktools.write_block(1, super_block)

    #def get_root_dir_inode(self):




if __name__ == '__main__':
    Format.get_disk_info(Format())

