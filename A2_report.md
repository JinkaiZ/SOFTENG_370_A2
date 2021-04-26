cd mount 

getattr / (None,) - gets the file attributes associated with / which is the mount directory.
The output is a dictionary. st_ctime is the creation time, st_mtime is the modified time,
st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file
access mode.

access / (1,) - checks the accessibility of the mount directory. Comes back with 0 which
means ok

{DEBUG:fuse.log-mixin:-> getattr / (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_ctime': 1617403556.219561,
'st_mtime': 1617403556.219561, 'st_nlink': 2, 'st_atime':
1617403556.219561, 'st_mode': 16877}
DEBUG:fuse.log-mixin:-> access / (1,)
DEBUG:fuse.log-mixin:<- access 0}

cat > hello 

getattr /hello (None,) - get the file attributes associated with /mount which is the hello file. The output gets the Errno 2 which is "No such file or directory". This is because that the file hello has not been created yet. 

create /hello (33204,) - create a file named "hello" with the file access mode is 33204 under the path /mount. The out put return the opreation name and the file descriptor which is fd = 1. 

getattr /hello (1,) - get the file attributes associated with /mount/hello which is the hello file. The output  is a dictionary. st_ctime is the creation time, st_mtime is the modified time, st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file access mode.

flush /hello (1,) - flush any pending changes to the file associated with /mount/hello which is the hello file. The return 0 means the flush operation is complete.  



{DEBUG:fuse.log-mixin:-> getattr /hello (None,)
DEBUG:fuse.log-mixin:<- getattr '[Errno 2] No such file or directory'
DEBUG:fuse:FUSE operation getattr raised a <class 'fuse.FuseOSError'>, returning errno 2.
Traceback (most recent call last):
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 734, in _wrapper
    return func(*args, **kwargs) or 0
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 774, in getattr
    return self.fgetattr(path, buf, None)
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 1027, in fgetattr
    attrs = self.operations('getattr', self._decode_optional_path(path), fh)
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 1251, in __call__
    ret = getattr(self, op)(path, *args)
  File "memory.py", line 55, in getattr
    raise FuseOSError(ENOENT)
fuse.FuseOSError: [Errno 2] No such file or directory
DEBUG:fuse.log-mixin:-> create /hello (33204,)
DEBUG:fuse.log-mixin:<- create 1
DEBUG:fuse.log-mixin:-> getattr /hello (1,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 33204, 'st_nlink': 1, 'st_size': 0, 'st_ctime': 1619147542.9163284, 'st_mtime': 1619147542.9163287, 'st_atime': 1619147542.916329}
DEBUG:fuse.log-mixin:-> flush /hello (1,)
DEBUG:fuse.log-mixin:<- flush 0}

hello world 

getxattr /hello ('security.capability',) - get the extended attributes which is the security capability attributes of the hello file(/mount/hello). The output returns ''.

write /hello (b'hello world\n', 0, 1) - write "hello world\n" into the file(/mount/hello) with a offset of 0 and the file handler = 1.  The output return the length of the input data (the number of items in a container) which is 12.  

{DEBUG:fuse.log-mixin:-> getxattr /hello ('security.capability',)
DEBUG:fuse.log-mixin:<- getxattr ''
DEBUG:fuse.log-mixin:-> write /hello (b'hello world\n', 0, 1)
DEBUG:fuse.log-mixin:<- write 12}

^D 

flush /hello (1,) - Close the hello file and flush any pending changes to the file associated with /mount/hello. The return 0 means the flush operation is complete. 

release /hello (1,) - Release the open file associated with /mount/hello which is the hello file with fd = 1. As there are no more references to the hello file. The file descriptors are closed and all memory mappings are unmapped. The return 0 means the release operation is complete.

DEBUG:fuse.log-mixin:-> flush /hello (1,)
DEBUG:fuse.log-mixin:<- flush 0
DEBUG:fuse.log-mixin:-> release /hello (1,)
DEBUG:fuse.log-mixin:<- release 0

ls -al

getattr / (None,) - gets the file attributes associated with / which is the mount directory.
The output is a dictionary. st_ctime is the creation time, st_mtime is the modified time,
st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file
access mode.

opendir / () - Open the directory associated with / which is the mount directory for reading. The  output return a numerical file handle. 

readdir / (0,) - yield directory entries for each file in the directory associated with / which is the mount directory with the file handle 0. The output returns a list of file/directory names inside the mount directory in the format of ['.', '..', 'List of file names']

getattr / (None,) - gets the file attributes associated with / which is the mount directory.
The output is a dictionary. st_ctime is the creation time, st_mtime is the modified time,
st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file
access mode.

getxattr / ('security.selinux',)- get the extended attributes which is the security.selinux attributes of the directory associated with / which is the mount directory. The output returns '' and throw an exception from FUSE operation getxattr, returning errno.EINVAL.

getattr /hello (None,) - get the file attributes associated with /mount/hello which is the hello file. The output  is a dictionary. st_ctime is the creation time, st_mtime is the modified time, st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file access mode.

getxattr /hello ('system.posix_acl_access',) - get the extended attribute 'system.posix_acl_access' of the hello file(/mount/hello). The output returns ''.  

releasedir / (0,) - Release the open directory associated with / which is the mount directory.  The return 0 means the release operation is complete.

{EBUG:fuse.log-mixin:-> getattr / (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 16877, 'st_ctime': 1619147846.8163872, 'st_mtime': 1619147846.8163872, 'st_atime': 1619147846.8163872, 'st_nlink': 2}
DEBUG:fuse.log-mixin:-> opendir / ()
DEBUG:fuse.log-mixin:<- opendir 0
DEBUG:fuse.log-mixin:-> readdir / (0,)
DEBUG:fuse.log-mixin:<- readdir ['.', '..', 'hello']
DEBUG:fuse.log-mixin:-> getattr / (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 16877, 'st_ctime': 1619147846.8163872, 'st_mtime': 1619147846.8163872, 'st_atime': 1619147846.8163872, 'st_nlink': 2}
DEBUG:fuse.log-mixin:-> getxattr / ('security.selinux',)
DEBUG:fuse.log-mixin:<- getxattr ''
ERROR:fuse:Uncaught exception from FUSE operation getxattr, returning errno.EINVAL.
Traceback (most recent call last):
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 734, in _wrapper
    return func(*args, **kwargs) or 0
  File "/home/jinkai/.local/lib/python3.8/site-packages/fuse.py", line 922, in getxattr
    buf = ctypes.create_string_buffer(ret, retsize)
  File "/usr/lib/python3.8/ctypes/__init__.py", line 65, in create_string_buffer
    raise TypeError(init)
TypeError
DEBUG:fuse.log-mixin:-> getattr /hello (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 33204, 'st_nlink': 1, 'st_size': 12, 'st_ctime': 1619147864.697559, 'st_mtime': 1619147864.6975596, 'st_atime': 1619147864.6975596}
DEBUG:fuse.log-mixin:-> getxattr /hello ('system.posix_acl_access',)
DEBUG:fuse.log-mixin:<- getxattr ''
DEBUG:fuse.log-mixin:-> releasedir / (0,)
DEBUG:fuse.log-mixin:<- releasedir 0}

rm hello

getattr / (None,) - gets the file attributes associated with / which is the mount directory.
The output is a dictionary. st_ctime is the creation time, st_mtime is the modified time,
st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file
access mode.

getattr /hello (None,) - get the file attributes associated with /mount/hello which is the hello file. The output  is a dictionary. st_ctime is the creation time, st_mtime is the modified time, st_nlink is the number of hard links, st_atime is the last accessed time, st_mode is the file access mode.

access /hello (2,) - checks the accessibility of the hello file. Comes back with 0 which
means okay.

unlink /hello () - unlink the pointer to the hello file. There is no return statement for unlink function. The output is None. 

DEBUG:fuse.log-mixin:-> getattr / (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 16877, 'st_ctime': 1619147846.8163872, 'st_mtime': 1619147846.8163872, 'st_atime': 1619147846.8163872, 'st_nlink': 2}
DEBUG:fuse.log-mixin:-> getattr /hello (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 33204, 'st_nlink': 1, 'st_size': 12, 'st_ctime': 1619147864.697559, 'st_mtime': 1619147864.6975596, 'st_atime': 1619147864.6975596}
DEBUG:fuse.log-mixin:-> access /hello (2,)
DEBUG:fuse.log-mixin:<- access 0
DEBUG:fuse.log-mixin:-> unlink /hello ()
DEBUG:fuse.log-mixin:<- unlink None

Q3. Yes, we can use the chmod function to change the mode of the file to 777.  OR talk about the permission (allow_other)