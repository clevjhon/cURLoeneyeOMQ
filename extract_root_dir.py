import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    s_log_block_size = struct.unpack("<I", f.read(4))[0]
    block_size = 1024 << s_log_block_size
    
    # Read root inode (Inode 2 is at index 1 in the inode table)
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    # Check extent tree magic in i_block
    i_block = inode_data[40:100]
    magic = struct.unpack("<H", i_block[0:2])[0]
    
    if magic == 0xf30a:
        ee_start_lo = struct.unpack("<I", i_block[16:20])[0]
        print(f"  [EXT4] Root extent data block: {ee_start_lo}")
        
        f.seek(ee_start_lo * block_size)
        dir_block = f.read(block_size)
        
        offset = 0
        print("  [EXT4] Root Directory Contents:")
        while offset < len(dir_block) - 8:
            # Corrected unpack format: <IHBB (4 + 2 + 1 + 1 = 8 bytes)
            header = dir_block[offset:offset+8]
            if len(header) < 8:
                break
            inode_val, rec_len, name_len, file_type = struct.unpack("<IHBB", header)
            if inode_val == 0 or rec_len == 0:
                break
            name = dir_block[offset+8 : offset+8+name_len].decode('utf-8', errors='ignore')
            print(f"    -> {name} (Inode: {inode_val}, Type: {file_type})")
            offset += rec_len
