import struct

with open("mosfetq-dos.img", "rb") as f:
    boot_sector = f.read(512)

# Unpack standard FAT12/16 BPB fields
jump = boot_sector[0:3]
oem = boot_sector[3:11]
bytes_per_sec = struct.unpack("<H", boot_sector[11:13])[0]
sec_per_clus = boot_sector[13]
reserved_sec = struct.unpack("<H", boot_sector[14:16])[0]
num_fats = boot_sector[16]
root_entries = struct.unpack("<H", boot_sector[17:19])[0]
total_sec_16 = struct.unpack("<H", boot_sector[19:21])[0]
media = boot_sector[21]
sec_per_fat = struct.unpack("<H", boot_sector[22:24])[0]
sec_per_track = struct.unpack("<H", boot_sector[24:26])[0]
num_heads = struct.unpack("<H", boot_sector[26:28])[0]
hidden_sec = struct.unpack("<I", boot_sector[28:32])[0]
total_sec_32 = struct.unpack("<I", boot_sector[32:36])[0]

print("=== FAT BPB Analysis ===")
print(f"Bytes per Sector: {bytes_per_sec}")
print(f"Sectors per Cluster: {sec_per_clus}")
print(f"Reserved Sectors: {reserved_sec}")
print(f"Number of FATs: {num_fats}")
print(f"Root Directory Entries: {root_entries}")
print(f"Sectors per FAT: {sec_per_fat}")
print(f"Total Sectors (16-bit): {total_sec_16}")

root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
root_dir_offset = root_dir_sector * bytes_per_sec
print(f"Calculated Root Directory Offset: {root_dir_offset} (Sector {root_dir_sector})")
