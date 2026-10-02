import struct

with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << struct.unpack("<I", f.read(4))[0]
    
    # Block 4 start (mapped from extent tree root)
    block_num = 4
    f.seek(block_num * block_size)
    block_data = f.read(block_size)
    
    print(f"  [EXT4] Parsing Directory Entries in Block {block_num}:")
    offset = 0
    while offset < block_size - 8:
        inode, rec_len, name_len, file_type = struct.unpack("<IHBB", block_data[offset:offset+8])
        if rec_len == 0 or inode == 0 and rec_len < 8:
            break
        
        name = block_data[offset+8 : offset+8+name_len].decode('utf-8', errors='ignore')
        print(f"    -> Offset {offset}: Inode={inode}, RecLen={rec_len}, NameLen={name_len}, FileType={file_type}, Name='{name}'")
        
        offset += rec_len
