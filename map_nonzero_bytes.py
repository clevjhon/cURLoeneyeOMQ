with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << int.from_bytes(f.read(4), "little")
    
    f.seek(143360 + 256)
    inode_data = f.read(256)
    
    i_block = inode_data[40:100]
    if i_block[0:2] == b'\x0a\xf3':
        ee_start_lo = int.from_bytes(i_block[16:20], "little")
        f.seek(ee_start_lo * block_size)
        data = f.read(block_size)
        
        bp_offset = 19
        rec_len = 12288
        span_data = data[bp_offset : bp_offset + rec_len]
        
        print("  [EXT4] Mapping Non-Zero Byte Indices for BP Span:")
        for idx, byte in enumerate(span_data):
            if byte != 0:
                print(f"    -> Offset +{idx:<5} (Absolute: {bp_offset + idx}): 0x{byte:02x} ({byte})")
