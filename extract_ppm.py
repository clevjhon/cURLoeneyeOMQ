with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << int.from_bytes(f.read(4), "little")
    
    start_block = 1293
    file_size = 192015
    
    f.seek(start_block * block_size)
    ppm_data = f.read(file_size)
    
    with open("extracted_test.ppm", "wb") as out:
        out.write(ppm_data)
        
    print(f"  [EXT4] Successfully extracted {len(ppm_data)} bytes to extracted_test.ppm")
