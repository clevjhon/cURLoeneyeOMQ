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
        
        # Target slice starting at bp_offset (19)
        bp_offset = 19
        fragment = data[bp_offset : bp_offset + 16]
        
        print("  [EXT4] Unpacking BP Fragment Structure:")
        print(f"    -> Raw Bytes: {fragment.hex()}")
        
        # Attempt standard directory entry sub-header unpacking
        sub_inode, sub_rec_len, sub_name_len, sub_file_type = struct.unpack("<IHBB", fragment[:8])
        print(f"    -> Sub-Inode: {sub_inode}")
        print(f"    -> Sub-RecLen: {sub_rec_len}")
        print(f"    -> Sub-NameLen: {sub_name_len}")
        print(f"    -> Sub-FileType: {sub_file_type}")
        
        if sub_name_len > 0 and sub_name_len < 32:
            sub_name = fragment[8:8+sub_name_len].decode('utf-8', errors='ignore')
            print(f"    -> Sub-Name: {sub_name}")
