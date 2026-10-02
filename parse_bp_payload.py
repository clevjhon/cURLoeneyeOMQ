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
        
        # BP entry starts at offset 19
        bp_offset = 19
        print(f"  [EXT4] Inspecting BP Payload at offset {bp_offset}...")
        
        # Read a snippet of the payload following the name field
        # Header is 8 bytes, name 'BP' is 2 bytes (total 10 bytes minimum)
        payload_start = bp_offset + 10
        payload_sample = data[payload_start : payload_start + 64]
        
        print(f"    -> Raw Hex Payload: {payload_sample.hex()}")
        print(f"    -> ASCII Representation: {payload_sample}")
