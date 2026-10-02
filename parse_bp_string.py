import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    i_block = inode_data[40:100]
    if struct.unpack("<H", i_block[0:2])[0] == 0xf30a:
        ee_start_lo = struct.unpack("<I", i_block[16:20])[0]
        f.seek(ee_start_lo * block_size)
        data = f.read(block_size)
        
        bp_offset = 19
        rec_len = 12288
        
        # Extract 78-byte name starting right after the 8-byte header
        name_start = bp_offset + 8
        name_len = 78
        raw_name = data[name_start : name_start + name_len]
        decoded_name = raw_name.decode('utf-8', errors='ignore')
        
        print("  [EXT4] Decoding BP Identifier String:")
        print(f"    -> Full String (78 bytes): {decoded_name}")
        
        # Check what's immediately following the 12288-byte span
        next_offset = bp_offset + rec_len
        print(f"  [EXT4] Examining block offset immediately following span (+{next_offset}):")
        next_header = data[next_offset : next_offset + 8]
        if len(next_header) >= 8:
            n_inode, n_reclen, n_namelen, n_ftype = struct.unpack("<IHBB", next_header)
            print(f"    -> Next Entry Inode: {n_inode}")
            print(f"    -> Next Entry RecLen: {n_reclen}")
            print(f"    -> Next Entry NameLen: {n_namelen}")
            print(f"    -> Next Entry FileType: {n_ftype}")
