import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    # Read root inode (Inode 2 is at index 1 of the inode table)
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    i_block = inode_data[40:100]
    if struct.unpack("<H", i_block[0:2])[0] == 0xf30a:
        ee_start_lo = struct.unpack("<I", i_block[16:20])[0]
        f.seek(ee_start_lo * block_size)
        data = f.read(block_size)
        
        offset = 0
        print("  [EXT4] Full Block Directory Scan:")
        while offset < block_size:
            header = data[offset:offset+8]
            if len(header) < 8:
                break
            inode_val, rec_len, name_len, file_type = struct.unpack("<IHBB", header)
            if rec_len == 0:
                break
            if inode_val != 0 and name_len > 0:
                name = data[offset+8 : offset+8+name_len].decode('utf-8', errors='ignore')
                print(f"    -> File: {name:<16} | Inode: {inode_val:<6} | Type: {file_type}")
            offset += rec_len
