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

unlink /hello () - unlink to the hello file. Pop out the data form files and data dictionaries. There is no return statement for unlink function. The output is None. 

DEBUG:fuse.log-mixin:-> getattr / (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 16877, 'st_ctime': 1619147846.8163872, 'st_mtime': 1619147846.8163872, 'st_atime': 1619147846.8163872, 'st_nlink': 2}
DEBUG:fuse.log-mixin:-> getattr /hello (None,)
DEBUG:fuse.log-mixin:<- getattr {'st_mode': 33204, 'st_nlink': 1, 'st_size': 12, 'st_ctime': 1619147864.697559, 'st_mtime': 1619147864.6975596, 'st_atime': 1619147864.6975596}
DEBUG:fuse.log-mixin:-> access /hello (2,)
DEBUG:fuse.log-mixin:<- access 0
DEBUG:fuse.log-mixin:-> unlink /hello ()
DEBUG:fuse.log-mixin:<- unlink None

Q2. Get the real user and group ids by using os.getuid() and os.getgid(). Call the chown(os.getuid(),os.getgid()) function inside the create(path,mode) and mkdir(path, mode) functions. 

Q3. Yes, we did not make any changes to access() function, and the FUSE default access() function has nothing in it so the file system does not check any access permissions.

Q4. I use a bitmap(16 bits) to keep track of free blocks. The initial integer value of the bitmap is 0.  In the format.py, the function initial_free_bitmap()  will loop through each block in my-disk. If the block is empty, the corresponding binary bit value will be set to 1. If the block is not empty, the value will be 0.  And then it will manually set the value to 0 at the position 0 because the next opeartion is write the bitmap into the first two bytes of block 0(Block_0[0:2]). This function will only be called once when the format.py is runed as mian. 

In the format.py, the function get_free_block(num_of_blocks) will return a integer array of free block indexs. When i need select one new free block, the value 1 will be passed into the function(get_free_block(1)). First, the bitmap in block_0[0:2] will be read in integer. The integer value will be transfer to binary. Each bit value of the binary bitmap will be appended into an integer array in a reversed order.(e.g [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]). The function will loop through the array and return the position index of the first values that is equal to 1. The position index value will be appended into an integer array as sometime it may need more than one free block. For the example above, the return value will be [2].  

In the small.py, the write_block function will be put inside a for loop to write data into selected free blocks. Then the update_bit_map(used_block) function in the format.py will update the bitmap through the bit manipulation function in bit.py.  Finally, the updated bitmap will be store back to the block_0[0:2]. 

 

Q5.  I also use a bitmap(16bits) to keep track of blocks allocated to a file. The block information is store in the "Location[23:25]" bytes positon of each metadata file. The initial integer value of the bitmap is 0. In the format.py, the function set_data_block_bitmap(block_num_array) will set the value to 1 for the bits which are coresponding to the block position index of the data blocks for that file. For example, a file stores data in block_3, the data bitmap will be [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0]. 

When we need to find a particular block of data associated with a file, we will read the "Location" bytes(Block[23:25]) of the metadata file and get the integer value of the bitmap. Then the integer value will be trasfer to binary value and each of the bit will be appended into an integer array in reversed order. A for loop will be use to loop through the integer array and return the position index value of the bit value which is equal to 1. The position index is the block number of the particular block of data associated with that file. The position indexs will also be appended into an integer array as there may have more than one blocks that save data for that file. 

Q6.  The file name and all other file attributes will be stored in one block at the specified position(Block[25:41]). There is only one file name in that block, so the unique file name corresponds to all the metadata of that file. 

I use a for loop to get the string value of the data which are stored at the position of file name(block[NAME_START:NAME_FINISH] ) for each block. Use an if statement to compare the specified file name with all the file names. If the result is true, it will return the block number(i) which is the block that stores all metadata for that file. Then use the read_block(i) function to read that whole block. Finally, use the slice function to read the bytes at the specific position which is the other attributes for that file. For example, block = read_block(1), block[2:4] will be the mode for the file. All the metada location information can be founded at the beginning of the format.py  

  

 