import struct

with open("mosfetq-dos.img", "rb") as f:
    root_dir_offset = 35 * 512
    root_entries = 224
    
    f.seek(root_dir_offset)
    root_dir_data = f.read(root_entries * 32)

    print("[*] Root Directory Entries (Fixed Offset):")
    for i in range(0, len(root_dir_data), 32):
        entry = root_dir_data[i:i+32]
        if entry[0] == 0x00: # End of directory
            break
        if entry[0] == 0xE5: # Deleted entry
            continue
        name = entry[0:11]
        attr = entry[11]
        cluster = struct.unpack("<H", entry[26:28])[0]
        size = struct.unpack("<I", entry[28:32])[0]
        print(f"    - Name: {name} | Attr: {attr:02x} | Cluster: {cluster} | Size: {size}")
