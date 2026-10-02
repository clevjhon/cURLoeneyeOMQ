import struct

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
        # Secondary cluster resides at relative offsets +37 to +40
        cluster_bytes = data[bp_offset + 37 : bp_offset + 41]
        
        print("  [EXT4] Decoding Secondary Anchor Cluster (+37 to +40):")
        print(f"    -> Raw Hex: {cluster_bytes.hex()}")
        
        # Unpack as little-endian 32-bit unsigned integer
        val_32 = struct.unpack("<I", cluster_bytes)[0]
        print(f"    -> Unpacked 32-bit Value: {val_32} (0x{val_32:08x})")
        
        # Check what resides at this absolute offset within the block if treated as a pointer
        if val_32 < block_size:
            target_slice = data[val_32 : val_32 + 8]
            print(f"    -> Target slice at offset {val_32}: {target_slice.hex()}")
