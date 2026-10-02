with open("oeneye-mosfetq-fat12.img", "rb") as f:
    data = f.read()

bytes_per_sec = int.from_bytes(data[11:13], "little")
sec_per_clus = data[13]
rsvd_sec = int.from_bytes(data[14:16], "little")
num_fats = data[16]
root_ent_cnt = int.from_bytes(data[17:19], "little")
fat_size_sec = int.from_bytes(data[22:24], "little")

root_dir_sectors = (root_ent_cnt * 32 + bytes_per_sec - 1) // bytes_per_sec
first_root_dir_sec = rsvd_sec + (num_fats * fat_size_sec)
first_root_dir_byte = first_root_dir_sec * bytes_per_sec
first_data_sector = first_root_dir_sec + root_dir_sectors
first_data_byte = first_data_sector * bytes_per_sec
clus_size = sec_per_clus * bytes_per_sec

def parse_dir(dir_offset, max_entries):
    for i in range(max_entries):
        entry_offset = dir_offset + (i * 32)
        entry = data[entry_offset:entry_offset+32]
        if entry[0] == 0x00: break
        if entry[0] == 0xE5: continue
        attr = entry[11]
        if attr == 0x0F: continue # Long file name entry
        
        name = entry[0:8].decode("ascii", errors="ignore").strip()
        ext = entry[8:11].decode("ascii", errors="ignore").strip()
        cluster = int.from_bytes(entry[26:28], "little")
        size = int.from_bytes(entry[28:32], "little")
        
        full_name = f"{name}.{ext}" if ext else name
        print(f"Entry: {full_name} | Attr: {attr} | Cluster: {cluster} | Size: {size}")
        
        if size == 4096 or "OMQ" in full_name or "FNT" in full_name:
            if cluster >= 2:
                file_offset = first_data_byte + (cluster - 2) * clus_size
                file_data = data[file_offset:file_offset+4096]
                with open("assets/fonts/OMQ.FNT", "wb") as out:
                    out.write(file_data)
                print(f"==> Extracted {full_name} ({len(file_data)} bytes) to assets/fonts/OMQ.FNT")

print("--- Scanning Root Directory ---")
parse_dir(first_root_dir_byte, root_ent_cnt)
