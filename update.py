with open("emu_dos.py", "r") as f:
    code = f.read()

map_func = """
def run_map():
    if not os.path.exists(IMAGE_PATH):
        print("[-] Error: Volume image missing.")
        return
    with open(IMAGE_PATH, "rb") as f:
        geo = get_disk_geometry(f)
        fat_offset = geo['reserved_sec'] * geo['bytes_per_sec']
        f.seek(fat_offset)
        fat_data = f.read(geo['sec_per_fat'] * geo['bytes_per_sec'])
        print(f"\\n--- FAT CLUSTER MAP (First 128 clusters) ---")
        cluster_grid = []
        for cluster in range(0, 128):
            if cluster < 2:
                status = "R"
            else:
                byte_idx = int(cluster * 1.5) if len(fat_data) > 4096 else cluster * 2
                if byte_idx + 2 <= len(fat_data):
                    val = struct.unpack("<H", fat_data[byte_idx:byte_idx+2])[0]
                    if len(fat_data) <= 4096:
                        val = val & 0xFFF
                    if val == 0x000:
                        status = "."
                    elif val >= 0xFF8:
                        status = "E"
                    else:
                        status = "X"
                else:
                    status = "?"
            cluster_grid.append(status)
        for r in range(0, len(cluster_grid), 32):
            row_str = " ".join(cluster_grid[r:r+32])
            print(f"{r:03X}: {row_str}")
        print("Legend: [.] Free  [X] Allocated  [E] End-Chain  [R] Reserved")
        print("-" * 65)
"""

if "def run_map" not in code:
    code = code.replace("def main():", map_func + "\ndef main():")
    code = code.replace('elif cmd == "TREE":\n            run_tree()', 'elif cmd == "TREE":\n            run_tree()\n        elif cmd == "MAP":\n            run_map()')
    code = code.replace('DIR, TREE', 'DIR, TREE, MAP')

    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("[+] emu_dos.py updated with MAP command successfully!")
else:
    print("[*] MAP command already present.")
