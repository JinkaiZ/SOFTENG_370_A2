#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging
import os
import sys
from format import Format, MODE_START, MODE_FINISH, CTIME_START, CTIME_FINISH,MTIME_START,MTIME_FINISH,NLINK_START,NLINK_FINISH, ATIME_START, ATIME_FINISH
import disktools
from collections import defaultdict
from errno import ENOENT
from stat import S_IFDIR, S_IFLNK, S_IFREG
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

BLOCK_SIZE = 64

if not hasattr(__builtins__, 'bytes'):
    bytes = str


class Small(LoggingMixIn, Operations):
    'Example memory filesystem. Supports only one level of files.'

    def __init__(self):
        block = disktools.read_block(0)
        if disktools.bytes_to_int(block[2:44]) == 0:
            self.files = {}
            self.data = defaultdict(bytes)
            self.fd = 0
            now = time()
            self.files['/'] = dict(
                st_mode=(S_IFDIR | 0o755),
                st_ctime=now,
                st_mtime=now,
                st_atime=now,
                st_nlink=2)

            # get all the metadata for the root directory
            dir_name = '/'
            mode = self.files['/'].get('st_mode')
            ctime = self.files['/'].get('st_ctime')
            mtime = self.files['/'].get('st_mtime')
            atime = self.files['/'].get('st_atime')
            nlink = self.files['/'].get('st_nlink')
            size = sys.getsizeof(self.files['/'])
            uid = os.getuid()
            gid = os.getgid()
            # write all the metadata into disk
            inode_data = Format.set_inode(Format, dir_name, mode, ctime, mtime, atime, nlink, uid, gid,size,0)
            disktools.write_block(0, inode_data)
        else:
            self.files = Format.get_files(Format)
            self.data = Format.get_data(Format)
            self.fd = 0
            self.files['/'] = dict(
                st_mode=disktools.bytes_to_int(block[MODE_START:MODE_FINISH]),
                st_ctime=disktools.bytes_to_int(block[CTIME_START:CTIME_FINISH]),
                st_mtime=disktools.bytes_to_int(block[MTIME_START:MTIME_FINISH]),
                st_atime=disktools.bytes_to_int(block[ATIME_START:ATIME_FINISH]),
                st_nlink=disktools.bytes_to_int(block[NLINK_START:NLINK_FINISH]))

    def create(self, path, mode):

        self.files[path] = dict(
            st_mode=(S_IFREG | mode),
            st_nlink=1,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

        name = path
        mode = self.files[path].get('st_mode')
        ctime = self.files[path].get('st_ctime')
        mtime = self.files[path].get('st_mtime')
        atime = self.files[path].get('st_atime')
        nlink = self.files[path].get('st_nlink')
        size = self.files[path].get('st_size')
        uid = os.getuid()
        gid = os.getgid()

        num_array = Format.get_free_block(Format, 1)
        block_num = num_array[0]

        inode_data = Format.set_inode(Format, name, mode, ctime, mtime, atime, nlink, uid, gid, size, block_num)
        disktools.write_block(block_num, inode_data)
        Format.update_free_block_bitmap(Format)


        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):

        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def chmod(self, path, mode):
        self.files[path]['st_mode'] &= 0o770000
        self.files[path]['st_mode'] |= mode
        return 0

    def chown(self, path, uid, gid):
        self.files[path]['st_uid'] = uid
        self.files[path]['st_gid'] = gid


    def mkdir(self, path, mode):
        self.files[path] = dict(
            st_mode=(S_IFDIR | mode),
            st_nlink=2,
            st_size=0,
            st_ctime=time(),
            st_mtime=time(),
            st_atime=time())

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        return self.data[path][offset:offset + size]

    def readdir(self, path, fh):
            return ['.', '..'] + [x[1:] for x in self.files if x != '/']


    def readlink(self, path):
        return self.data[path]

    def removexattr(self, path, name):
        attrs = self.files[path].get('attrs', {})

        try:
            del attrs[name]
        except KeyError:
            pass        # Should return ENOATTR

    def rename(self, old, new):
        self.data[new] = self.data.pop(old)
        self.files[new] = self.files.pop(old)

    def rmdir(self, path):
        # with multiple level support, need to raise ENOTEMPTY if contains any files
        self.files.pop(path)
        self.files['/']['st_nlink'] -= 1

    def setxattr(self, path, name, value, options, position=0):
        # Ignore options
        attrs = self.files[path].setdefault('attrs', {})
        attrs[name] = value

    def statfs(self, path):
        return dict(f_bsize=512, f_blocks=4096, f_bavail=2048)

    def symlink(self, target, source):
        self.files[target] = dict(
            st_mode=(S_IFLNK | 0o777),
            st_nlink=1,
            st_size=len(source))

        self.data[target] = source

    def truncate(self, path, length, fh=None):
        # make sure extending the file fills in zero bytes
        self.data[path] = self.data[path][:length].ljust(
            length, '\x00'.encode('ascii'))
        self.files[path]['st_size'] = length


    def unlink(self, path):
        self.data.pop(path)
        self.files.pop(path)
        Format.clear_data_block(Format, path)
        Format.update_free_block_bitmap(Format)
        Format.clear_metadata_block(Format, path)
        Format.update_free_block_bitmap(Format)




    def utimens(self, path, times=None):
        now = time()
        atime, mtime = times if times else (now, now)
        self.files[path]['st_atime'] = atime
        self.files[path]['st_mtime'] = mtime

    def write(self, path, data, offset, fh):

        self.data[path] = (
            # make sure the data gets inserted at the right offset
            self.data[path][:offset].ljust(offset, '\x00'.encode('ascii'))
            + data
            # and only overwrites the bytes that data is replacing
            + self.data[path][offset + len(data):])
        self.files[path]['st_size'] = len(self.data[path])


        # get the length of input data
        size = len(data)
        # calculate the number of blocks that need to store the data
        no_of_blocks = (size // BLOCK_SIZE) + 1
        # get the free blocks
        num_array = Format.get_free_block(Format, no_of_blocks)
        # set the data block bitmap
        data_block_bitmap = Format.set_data_block_bitmap(Format, num_array)
        # get the input data
        input_data = self.data[path]

        # save the data to disk into the allocated blocks
        for i in range(no_of_blocks):
            if no_of_blocks == 1:
                disktools.write_block(num_array[i], input_data)
            else:
                disktools.write_block(num_array[i], input_data[i*64:i*64+64])
        # Add the data block bitmap into the metadata information
        Format.update_file_location(Format, path, data_block_bitmap)
        # update the st_size in the metadata
        Format.update_size(Format, path, self.files[path]['st_size'])
        # update the free block bitmap
        Format.update_free_block_bitmap(Format)

        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Small(), args.mount, foreground=True)
