with open("oeneye-ext4.img", "rb") as f:
    f.seek(1048)
    block_size = 1024 << int.from_bytes(f.read(4), "little")
    
    start_block = 1292
    file_size = 639
    
    f.seek(start_block * block_size)
    png_data = f.read(file_size)
    
    with open("extracted_test.png", "wb") as out:
        out.write(png_data)
        
    print(f"  [EXT4] Successfully extracted {len(png_data)} bytes to extracted_test.png")
    print(f"    -> PNG Magic Bytes: {png_data[:8].hex()}")
