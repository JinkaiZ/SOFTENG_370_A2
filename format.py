#!/usr/bin/env python
"""
    The format.py to use for Operating Systems Assignment 2 2021
    written by: Jinkai Zhang
                UPI: Jzha541

"""

import os
from stat import S_IFDIR
from time import time

import bits
import disktools
from collections import defaultdict
from errno import ENOENT


NUM_BLOCKS = 16
BLOCK_SIZE = 64

# Fix metadata locations in for root directory block
BITMAP_START = 0
BITMAP_FINISH = 2


# Fix metadata locations in for each block
MODE_START = 2
MODE_FINISH = 4
UID_START = 4
UID_FINISH = 6
GID_START = 6
GID_FINISH = 8
NLINK_START = 8
NLINK_FINISH = 9
CTIME_START = 9
CTIME_FINISH = 13
MTIME_START = 13
MTIME_FINISH = 17
ATIME_START = 17
ATIME_FINISH = 21
SIZE_START = 21
SIZE_FINISH = 23
LOCATION_START = 23
LOCATION_FINISH = 25
NAME_START = 25
NAME_FINISH = 64

class Format:


    def initial_disk(self):
        self.initial_free_block_bitmap(Format)
        self.initial_root_metadata(Format)

    def initial_root_metadata(self):
        now = time()
        name = '/'
        mode = (S_IFDIR | 0o755)
        ctime = now,
        mtime = now,
        atime = now,
        nlink = 2
        uid = os.getuid()
        gid = os.getgid()
        size = 0
        block_num = 0
        inode_data = self.set_inode(self, name, mode, ctime[0], mtime[0], atime[0], nlink, uid, gid, size, block_num)
        disktools.write_block(0, inode_data)


    """ loop through the disk and create the initial bitmap for the disk. 0 means used, 1 means free """
    def initial_free_block_bitmap(self):
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

        # set the first block to 1 which means it is not free(will store bitmap into block 0).
        bitmap = bits.clearBit(bitmap, 0)
        # write the bitmap value at the first two bytes at block 0
        bitmap_disk = disktools.read_block(0)
        bitmap_disk[BITMAP_START:BITMAP_FINISH] = disktools.int_to_bytes(bitmap, 2)
        disktools.write_block(0, bitmap_disk)

    """ pass a int array that represent the position index of the block which the state will be change """
    def update_bit_map(self, used_block):
        block = disktools.read_block(0)
        # get the int number of bitmap
        bitmap = disktools.bytes_to_int(block[BITMAP_START:BITMAP_FINISH])

        for i in used_block:
            bitmap = bits.toggleBit(bitmap, i)

        block[BITMAP_START:BITMAP_FINISH] = disktools.int_to_bytes(bitmap, 2)
        disktools.write_block(0, block)
        return bitmap

    """ pass a int array of the required number of free block, return a int array with the free block numbers """
    def get_free_block(self, num_of_blocks):
        block = disktools.read_block(0)
        bit_array = []
        free_block = []
        # get int value of bitmap
        bitmap_int = disktools.bytes_to_int(block[BITMAP_START:BITMAP_FINISH])
        # transfer the bitmap to binary
        bitmap_bin = bin(bitmap_int)
        # add each bit into a int array
        for b in bitmap_bin[2:]:
            bit_array.append(int(b))
        # reverse the order of the array
        bit_array = reversed(bit_array)
        # return the index of each bit which is 1
        for idx, val in enumerate(bit_array):
            if val == 1:
                free_block.append(idx)
        return free_block[0:num_of_blocks]

    """ set the medata of a file (position in block) """
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

    """ return the files which has the same data structure as the files in memory """
    def get_files(self):
        files = {}
        for i in range(1, NUM_BLOCKS, 1):
            block = disktools.read_block(i)
            if (block[NAME_START:NAME_FINISH].decode().rstrip('\x00') != '') & (disktools.bytes_to_int(block[0:2]) == 0):
                files[block[NAME_START:NAME_FINISH].decode().rstrip('\x00')] = dict(
                    st_mode=disktools.bytes_to_int(block[MODE_START:MODE_FINISH]),
                    st_nlink=disktools.bytes_to_int(block[NLINK_START:NLINK_FINISH]),
                    st_size=disktools.bytes_to_int(block[SIZE_START:SIZE_FINISH] ),
                    st_ctime=disktools.bytes_to_int(block[CTIME_START:CTIME_FINISH]),
                    st_mtime=disktools.bytes_to_int(block[MTIME_START:MTIME_FINISH]),
                    st_atime=disktools.bytes_to_int(block[ATIME_START:ATIME_FINISH]),
                    st_gid=disktools.bytes_to_int(block[GID_START:GID_FINISH]),
                    st_uid=disktools.bytes_to_int(block[UID_START:UID_FINISH])
                    )

        return files

    """ return the data which has the same data structure as the data in memory """
    def get_data(self):
        total_data = defaultdict(bytes)

        for i in range(1, NUM_BLOCKS, 1):
            file_data = []
            data_block = []
            num_array = []
            block = disktools.read_block(i)
            path = block[NAME_START:NAME_FINISH].decode().rstrip('\x00')
            # if the location bytes are not empty & the first two bytes are empty means the block saves metadata of a file.
            if (disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH]) != 0) & (disktools.bytes_to_int(block[0:2]) == 0):
                # get the bitmap of the location of the file data.
                block_number = disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH])
                block_number_bin = bin(block_number)

                for b in block_number_bin[2:]:
                    num_array.append(int(b))

                num_array = list(reversed(num_array))

                for idx, val in enumerate(num_array):
                    if val == 1:
                        data_block.append(idx)
                #read the data in each block
                for data in data_block:
                    file_content = disktools.read_block(data).decode().rstrip('\x00')
                    file_data.append(file_content)
                # combine all the data if needed.
                file_data = ''.join(map(str, file_data))
                file_data = file_data.encode()
                # form the same structure as the data variable in memory
                total_data[path] = (
                    file_data
                )

        return total_data

    """ update the location in metadata """
    def update_file_location(self, path, bitmap):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[LOCATION_START:LOCATION_FINISH] = disktools.int_to_bytes(bitmap, 2)
                disktools.write_block(i, block)

        return 0

    """ create the bitmap for indicating the data blocks"""
    def set_data_block_bitmap(self, block_num_array):
        # initialise the bitmap int value to 0
        bitmap = 0
        for i in block_num_array:
            bitmap = bits.setBit(bitmap, i)

        return bitmap

    """ update the size of metadata"""
    def update_size(self, path,size):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[SIZE_START:SIZE_FINISH] = disktools.int_to_bytes(size, 2)
                disktools.write_block(i, block)

        return 0

    """ update the name(path) of metadata"""
    def update_name(self, path,new_path):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[NAME_START:NAME_FINISH] = new_path.encode()
                disktools.write_block(i, block)

        return 0

    """ update the mode of metadata"""
    def update_mode(self, path, mode):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[MODE_START:MODE_FINISH] = disktools.int_to_bytes(mode, 2)
                disktools.write_block(i, block)

        return 0

    """ update the mtime of metadata"""
    def update_mtime(self, path, mtime):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[MTIME_START:MTIME_FINISH] = disktools.int_to_bytes(mtime, 4)
                disktools.write_block(i, block)

        return 0

    """ update the owner of metadata"""
    def update_owner(self, path, uid, gid):

        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                block[UID_START:UID_FINISH] = disktools.int_to_bytes(uid, 2)
                block[GID_START:GID_FINISH] = disktools.int_to_bytes(gid, 2)
                disktools.write_block(i, block)

        return 0

    """ update the st_nlink of metadata"""
    def update_nlink(self, path, update):

        for i in range(0,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                new_nlink = disktools.bytes_to_int(block[NLINK_START:NLINK_FINISH]) + update
                block[NLINK_START:NLINK_FINISH] = disktools.int_to_bytes(new_nlink, 1)
                disktools.write_block(i, block)

        return 0

    """ set the value to 0 for all byte for metadata block"""
    def clear_metadata_block(self, path):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                num_array = []
                clean_block = bytearray([0] * BLOCK_SIZE)
                disktools.write_block(i, clean_block)
                num_array.append(i)
                self.update_bit_map(self, num_array)

    """ set the value to 0 for all byte for data block"""
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

                    disktools.write_block(data, clean_block)

                self.update_bit_map(self, data_block)

    """ Check the file has data or not"""
    def check_file_data(self, path):
        for i in range(1,NUM_BLOCKS,1):
            block = disktools.read_block(i)
            if block[NAME_START:NAME_FINISH].decode().rstrip('\x00') == path:
                if disktools.bytes_to_int(block[LOCATION_START:LOCATION_FINISH]) != 0:
                    return True
                else:
                    return False

    """ check the path to see is there any '/' in it. """
    def check_path_name(self,path):
        flag = True
        for c in path:
            if c == '/':
                flag = False

        return flag

    """ Find the parent path """
    def find_parent_path(self, path):
        index = []
        if (path[0:1] == '/') & (self.check_path_name(self, path[1:])):
            return '/'
        else:
            for i, c in enumerate(path):
                if c == '/':
                    index.append(i)

            length = len(index)
            return path[0:index[length - 1]]





if __name__ == '__main__':
    Format.initial_disk(Format)

