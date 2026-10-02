import struct

with open("mosfetq-dos.img", "r+b") as f:
    f.seek(11)
    bytes_per_sec = struct.unpack("<H", f.read(2))[0]
    reserved_sec = struct.unpack("<H", f.read(2))[0]
    num_fats = f.read(1)[0]
    root_entries = struct.unpack("<H", f.read(2))[0]
    f.seek(22)
    sec_per_fat = struct.unpack("<H", f.read(2))[0]

    root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
    root_dir_offset = root_dir_sector * bytes_per_sec
    
    f.seek(root_dir_offset)
    root_dir_data = f.read(root_entries * 32)
    
    # Let's free up slots containing .LOG files
    cleaned = 0
    for i in range(0, len(root_dir_data), 32):
        entry = root_dir_data[i:i+32]
        if entry[0] == 0x00:
            break
        ext = entry[8:11].decode('ascii', errors='ignore').strip()
        if ext == "LOG":
            f.seek(root_dir_offset + i)
            f.write(b'\xE5' + b'\x00' * 31) # Mark as deleted/free slot (0xE5)
            cleaned += 1

print(f"[+] Freed {cleaned} log slots in the FAT12 root directory.")
