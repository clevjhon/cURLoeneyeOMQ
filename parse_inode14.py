import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    f.seek(block_size)
    bg_inode_table_lo = struct.unpack("<I", f.read(32)[8:12])[0]
    
    inode_table_offset = bg_inode_table_lo * block_size
    inode_size = 256
    
    target_offset = inode_table_offset + (13 * inode_size)
    f.seek(target_offset)
    inode_data = f.read(inode_size)
    
    i_mode = struct.unpack("<H", inode_data[0:2])[0]
    i_size_lo = struct.unpack("<I", inode_data[4:8])[0]
    i_links_count = struct.unpack("<H", inode_data[16:18])[0]
    
    print("  [EXT4] Inode 14 Metadata (test.ppm):")
    print(f"    -> Mode: 0x{i_mode:04x}")
    print(f"    -> Size: {i_size_lo} bytes")
    print(f"    -> Links Count: {i_links_count}")
    
    i_block = inode_data[40:100]
    eh_magic, eh_entries, eh_max, eh_depth = struct.unpack("<HHHH", i_block[:8])
    print(f"    -> Extent Magic: 0x{eh_magic:04x}, Entries: {eh_entries}, Depth: {eh_depth}")
    
    if eh_magic == 0xf30a and eh_depth == 0:
        for i in range(eh_entries):
            offset = 12 + (i * 12)
            ee_block, ee_len, ee_start_hi, ee_start_lo = struct.unpack("<IHHI", i_block[offset:offset+12])
            absolute_block = (ee_start_hi << 32) | ee_start_lo
            print(f"      * Extent {i}: File Block {ee_block}, Length {ee_len}, Start Block {absolute_block}")
