import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    # Read root inode
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    i_block = inode_data[40:100]
    if struct.unpack("<H", i_block[0:2])[0] == 0xf30a:
        ee_start_lo = struct.unpack("<I", i_block[16:20])[0]
        f.seek(ee_start_lo * block_size)
        data = f.read(block_size)
        
        bp_offset = 19
        rec_len = 12288
        span_data = data[bp_offset : bp_offset + rec_len]
        
        print(f"  [EXT4] Scanning 12288-byte span at offset {bp_offset}...")
        
        chunk_size = 64
        for i in range(0, len(span_data), chunk_size):
            chunk = span_data[i:i+chunk_size]
            if any(b != 0 for b in chunk):
                print(f"    -> Relative Offset +{i:<5}: {chunk[:16].hex()}")
