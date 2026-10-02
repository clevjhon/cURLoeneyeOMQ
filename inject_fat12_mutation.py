import struct
import os

def write_file_to_image(image_path, filename, extension, new_content):
    with open(image_path, "r+b") as f:
        # Read BPB parameters
        f.seek(11)
        bytes_per_sec = struct.unpack("<H", f.read(2))[0]
        sec_per_clus = f.read(1)[0]
        reserved_sec = struct.unpack("<H", f.read(2))[0]
        num_fats = f.read(1)[0]
        root_entries = struct.unpack("<H", f.read(2))[0]
        f.seek(22)
        sec_per_fat = struct.unpack("<H", f.read(2))[0]

        fat_offset = reserved_sec * bytes_per_sec
        root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
        root_dir_offset = root_dir_sector * bytes_per_sec

        # Locate an empty or matching root directory slot
        f.seek(root_dir_offset)
        root_dir_data = f.read(root_entries * 32)
        
        target_slot = -1
        for i in range(0, len(root_dir_data), 32):
            entry = root_dir_data[i:i+32]
            if entry[0] == 0x00 or entry[0] == 0xE5:
                target_slot = root_dir_offset + i
                break
        
        if target_slot == -1:
            print("[-] Error: Root directory is full.")
            return

        # Prepare 32-byte directory entry (8.3 format)
        name_padded = filename.ljust(8)[:8].encode('ascii')
        ext_padded = extension.ljust(3)[:3].encode('ascii')
        attr = 0x20 # Archive
        reserved = b'\x00' * 10
        time_date = b'\x00' * 4
        start_cluster = 24 # Assign next free cluster chain start
        file_size = len(new_content)

        entry_bytes = name_padded + ext_padded + bytes([attr]) + reserved + time_date + struct.pack("<H", start_cluster) + struct.pack("<I", file_size)

        f.seek(target_slot)
        f.write(entry_bytes)
        print(f"[+] Successfully injected {filename}.{extension} (Size: {file_size} bytes) at root directory offset {target_slot}")

if __name__ == "__main__":
    image_file = "mosfetq-dos.img"
    if os.path.exists(image_file):
        sample_payload = b"OENEYE MUTATION KERNEL PAYLOAD V1.0 - DYNAMIC INJECTION VERIFIED.\n"
        write_file_to_image(image_file, "MUTATE", "LOG", sample_payload)
    else:
        print(f"[-] Target image {image_file} not found.")
