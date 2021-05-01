#!/usr/bin/env python

import os
import bits
import disktools
from collections import defaultdict
from errno import ENOENT
from time import time


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
LOCATION_FINISH = 27
NAME_START = 27
NAME_FINISH = 43






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

    def set_inode(self, name, mode, ctime, mtime, atime, nlink, uid, gid, size, block_num):
        block = disktools.read_block(block_num)
        block[MODE_START:MODE_FINISH] = disktools.int_to_bytes(mode, 2)
        block[UID_START:UID_FINISH] = disktools.int_to_bytes(uid, 2)
        block[GID_START:GID_FINISH] = disktools.int_to_bytes(gid, 2)
        block[NLINK_START:NLINK_FINISH] = disktools.int_to_bytes(nlink, 1)
        block[SIZE_START:SIZE_FINISH] = disktools.int_to_bytes(size, 2)
        block[CTIME_START:CTIME_FINISH] = disktools.int_to_bytes(int(ctime), 4)
        block[MTIME_START:MTIME_FINISH] = disktools.int_to_bytes(int(mtime), 4)
        block[ATIME_START:ATIME_FINISH] = disktools.int_to_bytes(int(atime), 4)
        block[LOCATION_START:LOCATION_FINISH] = disktools.int_to_bytes(0,2)
        block[NAME_START:NAME_FINISH] = name.encode()

        return block

    def get_files(self):
        files = {}
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if (block[NAME_START:NAME_FINISH].decode().rstrip('\x00') != '') & disktools.bytes_to_int(block[0:2]) == 0:

                files[block[NAME_START:NAME_FINISH].decode().rstrip('\x00')] = dict(
                    st_mode=disktools.bytes_to_int(block[MODE_START:MODE_FINISH]),
                    st_nlink=disktools.bytes_to_int(block[NLINK_START:NLINK_FINISH]),
                    st_size=disktools.bytes_to_int(block[SIZE_START:SIZE_FINISH] ),
                    st_ctime=disktools.bytes_to_int(block[CTIME_START:CTIME_FINISH]),
                    st_mtime=disktools.bytes_to_int(block[MTIME_START:MTIME_FINISH]),
                    st_atime=disktools.bytes_to_int(block[ATIME_START:ATIME_FINISH])
                    )

        return files

    def get_data(self):
        total_data =  defaultdict(bytes)
        for i in range(1,NUM_BLOCKS,1):
            file_data = []
            data_block = []
            num_array = []
            block = disktools.read_block(i)
            path = block[NAME_START:NAME_FINISH].decode().rstrip('\x00')


            if (disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH]) != 0) & disktools.bytes_to_int(block[0:2]) == 0:
                block_number = disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH])
                block_number_bin = bin(block_number)


                for b in block_number_bin[2:]:
                    num_array.append(int(b))

                num_array = list(reversed(num_array))


                for idx, val in enumerate(num_array):
                    if val == 1:
                        data_block.append(idx)


                for data in data_block:
                    print(disktools.read_block(data))
                    file_content = disktools.read_block(data).decode().rstrip('\x00')

                    file_data.append(file_content)


                file_data = ''.join(map(str, file_data))
                file_data = file_data.encode()
                total_data[path] = (
                    file_data
                )

        return total_data

    def update_file_location(self, path, bitmap):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[LOCATION_START:LOCATION_FINISH] = disktools.int_to_bytes(bitmap, 2)
                disktools.write_block(i, block)

        return 0

    def set_data_block_bitmap(self, block_num_array):
        # initialise the bitmap int value to 0
        bitmap = 0
        for i in block_num_array:
            bitmap = bits.setBit(bitmap, i)

        return bitmap

    def update_size(self, path,size):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[SIZE_START:SIZE_FINISH] = disktools.int_to_bytes(size, 2)
                disktools.write_block(i, block)

        return 0

    def get_block(self, path):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                return i

    def clear_metadata_block(self, path):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                clean_block = bytearray([0] * BLOCK_SIZE)
                disktools.write_block(i, clean_block)

    def clear_data_block(self, path):
        for i in range(1,NUM_BLOCKS,1):
            data_block = []
            num_array = []
            clean_block = bytearray([0] * BLOCK_SIZE)
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:

                block_number = disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH])
                block_number_bin = bin(block_number)

                for b in block_number_bin[2:]:
                    num_array.append(int(b))

                num_array = list(reversed(num_array))

                for idx, val in enumerate(num_array):
                    if val == 1:
                        data_block.append(idx)

                for data in data_block:
                    print(data)
                    disktools.write_block(data, clean_block)








if __name__ == '__main__':
    Format.initial_bitmap(Format)
    Format.update_free_block_bitmap(Format)

    a = Format.clear_data_block(Format, '/file3')

    #b = [2,3,4]
    #a = Format.set_data_block_bitmap(Format,b)
    #a = Format.get_free_block(Format, 1)
    print(a)

    # block = disktools.read_block(1)
