import struct

def get_fat_value(fat_data, cluster):
    # FAT12 packs two cluster entries into 3 bytes
    fat_offset = cluster + (cluster // 2)
    if fat_offset + 1 >= len(fat_data):
        return 0xFFF
    
    val = struct.unpack("<H", fat_data[fat_offset:fat_offset+2])[0]
    if cluster & 1:
        val >>= 4
    else:
        val &= 0xFFF
    return val

def extract_file():
    with open("mosfetq-dos.img", "rb") as f:
        # Read BPB parameters
        f.seek(11)
        bytes_per_sec = struct.unpack("<H", f.read(2))[0]
        sec_per_clus = f.read(1)[0]
        reserved_sec = struct.unpack("<H", f.read(2))[0]
        num_fats = f.read(1)[0]
        root_entries = struct.unpack("<H", f.read(2))[0]
        f.seek(22)
        sec_per_fat = struct.unpack("<H", f.read(2))[0]

        # Calculate FAT and Data region offsets
        fat_offset = reserved_sec * bytes_per_sec
        fat_size = sec_per_fat * bytes_per_sec
        
        root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
        root_dir_offset = root_dir_sector * bytes_per_sec
        
        # Data region starts after the root directory
        root_dir_sectors = (root_entries * 32 + bytes_per_sec - 1) // bytes_per_sec
        first_data_sector = root_dir_sector + root_dir_sectors
        
        # Read FAT table
        f.seek(fat_offset)
        fat_data = f.read(fat_size)

        # Locate BIG.TXT in root directory
        f.seek(root_dir_offset)
        root_dir_data = f.read(root_entries * 32)
        
        cluster = 0
        file_size = 0
        for i in range(0, len(root_dir_data), 32):
            entry = root_dir_data[i:i+32]
            if entry[0] == 0x00:
                break
            if entry[0] == 0xE5:
                continue
            if entry[0:11] == b"BIG     TXT":
                cluster = struct.unpack("<H", entry[26:28])[0]
                file_size = struct.unpack("<I", entry[28:32])[0]
                break

        print(f"[*] Extracting BIG.TXT (Starting Cluster: {cluster}, Size: {file_size} bytes)")

        # Traverse cluster chain and read data
        cluster_bytes = sec_per_clus * bytes_per_sec
        file_data = bytearray()

        while cluster >= 2 and cluster < 0xFF8:
            # Sector for cluster N = first_data_sector + (cluster - 2) * sec_per_clus
            sector = first_data_sector + (cluster - 2) * sec_per_clus
            f.seek(sector * bytes_per_sec)
            file_data.extend(f.read(cluster_bytes))
            
            # Get next cluster from FAT12
            cluster = get_fat_value(fat_data, cluster)

        # Truncate to exact file size
        file_data = file_data[:file_size]

        # Save extracted content
        output_name = "extracted_big.txt"
        with open(output_name, "wb") as out:
            out.write(file_data)
        print(f"[+] Successfully extracted {len(file_data)} bytes to {output_name}")

if __name__ == "__main__":
    extract_file()
