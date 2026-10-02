import struct

with open("mosfetq-dos.img", "rb") as f:
    f.seek(11)
    bytes_per_sec = struct.unpack("<H", f.read(2))[0]
    sec_per_clus = f.read(1)[0]
    reserved_sec = struct.unpack("<H", f.read(2))[0]
    num_fats = f.read(1)[0]
    root_entries = struct.unpack("<H", f.read(2))[0]
    
    f.seek(22)
    sec_per_fat = struct.unpack("<H", f.read(2))[0]

    root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
    root_dir_offset = root_dir_sector * bytes_per_sec

    f.seek(root_dir_offset)
    root_dir_data = f.read(root_entries * 32)

    print(f"[*] Root Dir Offset: {root_dir_offset} | Entries: {root_entries} | Read Bytes: {len(root_dir_data)}")
    print("[*] Scanning Volume Root Directory:")
    
    for i in range(0, len(root_dir_data), 32):
        entry = root_dir_data[i:i+32]
        if not entry or len(entry) < 32:
            break
        if entry[0] == 0x00:
            continue  # Skip empty slots instead of breaking early
        if entry[0] == 0xE5:
            continue  # Deleted entry
        
        name = entry[0:8].decode('ascii', errors='ignore').strip()
        ext = entry[8:11].decode('ascii', errors='ignore').strip()
        attr = entry[11]
        
        if attr == 0x0F:  # Skip LFN entries
            continue
            
        size = struct.unpack("<I", entry[28:32])[0]
        cluster = struct.unpack("<H", entry[26:28])[0]
        print(f"  -> Found: {name}.{ext} | Cluster: {cluster} | Size: {size} bytes | Slot: {i}")

if __name__ == "__main__":
    pass
