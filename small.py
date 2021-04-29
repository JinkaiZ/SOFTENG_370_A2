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
            inode_data = Format.set_inode(Format, dir_name, mode, ctime, mtime, atime, nlink, uid, gid,size)
            disktools.write_block(0, inode_data)
        else:
            self.files = {}
            self.data = defaultdict(bytes)
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
        size = sys.getsizeof(self.files[path])
        uid = os.getuid()
        gid = os.getgid()

        inode_data = Format.set_inode(Format, name, mode, ctime, mtime, atime, nlink, uid, gid, size)
        disktools.write_block(1, inode_data)

        self.fd += 1
        return self.fd

    def getattr(self, path, fh=None):
        if path not in self.files:
            raise FuseOSError(ENOENT)

        return self.files[path]

    def getxattr(self, path, name, position=0):
        attrs = self.files[path].get('attrs', {})

        try:
            return attrs[name]
        except KeyError:
            return ''       # Should return ENOATTR

    def listxattr(self, path):
        attrs = self.files[path].get('attrs', {})
        return attrs.keys()

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
        return len(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse = FUSE(Small(), args.mount, foreground=True)
