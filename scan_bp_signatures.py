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
        span_data = data[bp_offset : bp_offset + rec_len]
        
        print("  [EXT4] Scanning BP Span for Known Signatures...")
        
        # Check for ELF signature (7f 45 4c 46)
        elf_idx = span_data.find(b'\x7fELF')
        if elf_idx != -1:
            print(f"    -> Found ELF signature at relative offset +{elf_idx}")
            
        # Check for gzip signature (1f 8b)
        gz_idx = span_data.find(b'\x1f\x8b')
        if gz_idx != -1:
            print(f"    -> Found GZIP signature at relative offset +{gz_idx}")
            
        # Scan for any non-zero sequences or printable strings longer than 4 chars
        print("    -> Scan complete. Analyzing density bounds...")
        non_zero_count = sum(1 for b in span_data if b != 0)
        print(f"    -> Non-zero byte count within 12288 span: {non_zero_count}")
