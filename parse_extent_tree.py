import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    # Read Inode 2 (Root directory inode)
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    # i_block field is located at offset 40 to 100 within the inode
    i_block = inode_data[40:100]
    
    print("  [EXT4] Parsing Extent Tree Root in Inode 2 i_block:")
    
    # Extent header structure: magic (2 bytes), entries (2 bytes), max (2 bytes), depth (2 bytes), generation (4 bytes)
    eh_magic, eh_entries, eh_max, eh_depth, eh_generation = struct.unpack("<HHHHI", i_block[:12])
    
    print(f"    -> Magic: 0x{eh_magic:04x}")
    print(f"    -> Entries: {eh_entries}")
    print(f"    -> Max Entries: {eh_max}")
    print(f"    -> Depth: {eh_depth}")
    print(f"    -> Generation: {eh_generation}")
    
    if eh_magic == 0xf30a:
        print("    -> Extent magic signature valid.")
        
        # If depth is 0, entries are leaf extents (12 bytes each)
        if eh_depth == 0:
            for i in range(eh_entries):
                offset = 12 + (i * 12)
                ee_block, ee_len, ee_start_hi, ee_start_lo = struct.unpack("<IHHI", i_block[offset:offset+12])
                absolute_block = (ee_start_hi << 32) | ee_start_lo
                print(f"      * Extent {i}: File Block {ee_block}, Length {ee_len}, Start Block {absolute_block}")
        else:
            print("    -> Depth > 0: Index extents present. Further traversal required.")
