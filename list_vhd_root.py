import os

def list_root(image_path="mosfetq-dos.img"):
    with open(image_path, "rb") as f:
        f.seek(11)
        bytes_per_sector = int.from_bytes(f.read(2), "little")
        reserved_sectors = int.from_bytes(f.read(2), "little")
        num_fats = f.read(1)[0]
        root_entry_count = int.from_bytes(f.read(2), "little")
        f.seek(22)
        sectors_per_fat = int.from_bytes(f.read(2), "little")

        root_dir_sector = reserved_sectors + (num_fats * sectors_per_fat)
        root_dir_offset = root_dir_sector * bytes_per_sector
        root_dir_size = (root_entry_count * 32)

        f.seek(root_dir_offset)
        root_dir_data = f.read(root_dir_size)

        print("[*] Root Directory Entries:")
        for i in range(0, len(root_dir_data), 32):
            entry = root_dir_data[i:i+32]
            if entry[0] == 0x00: # End of directory
                break
            if entry[0] == 0xE5: # Deleted entry
                continue
            name = entry[0:11]
            attr = entry[11]
            size = int.from_bytes(entry[28:32], "little")
            print(f"    - Name: {name} | Attr: {attr:02x} | Size: {size}")

if __name__ == "__main__":
    list_root()
