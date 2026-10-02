import struct

with open("oeneye-ext4.img", "rb") as f:
    # Read block size
    f.seek(1048)
    s_log_block_size = struct.unpack("<I", f.read(4))[0]
    block_size = 1024 << s_log_block_size
    
    # In ext4, group descriptor table usually starts at block 1 (offset = block_size)
    f.seek(block_size)
    # Read block group descriptor 0 to find inode table location
    bg_desc = f.read(32)
    bg_inode_table = struct.unpack("<I", bg_desc[8:12])[0]
    inode_table_offset = bg_inode_table * block_size
    
    print(f"  [EXT4] Inode table located at offset: {inode_table_offset}")
    
    # Read root inode (Inode 2 is typically the root directory in ext4)
    # Each inode is 256 bytes by default in modern ext4
    f.seek(inode_table_offset + (2 - 1) * 256)
    root_inode = f.read(256)
    
    # Extract file size and block pointers from root inode
    i_size_lo = struct.unpack("<I", root_inode[4:8])[0]
    print(f"  [EXT4] Root directory data size: {i_size_lo} bytes")

print("Filesystem structure mapped successfully. Ready for full extraction.")
