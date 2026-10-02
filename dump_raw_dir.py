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
        print("  [EXT4] Raw Directory Dump:")
        while offset < block_size - 8:
            header = data[offset:offset+8]
            inode_val, rec_len, name_len, file_type = struct.unpack("<IHBB", header)
            if rec_len == 0:
                break
            name = data[offset+8 : offset+8+name_len].decode('utf-8', errors='ignore') if name_len > 0 else "<empty>"
            print(f"    Offset: {offset:<4} | Inode: {inode_val:<5} | RecLen: {rec_len:<4} | NameLen: {name_len:<3} | Name: {name}")
            offset += rec_len
