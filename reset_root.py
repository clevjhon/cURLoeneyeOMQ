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
    
    # Zero out the entire root directory table
    f.seek(root_dir_offset)
    f.write(b'\x00' * (root_entries * 32))

print("[+] Successfully reset and cleared the entire FAT12 root directory table!")
