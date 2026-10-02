with open("emu.py", "r") as f:
    code = f.read()

mount_command = """
        elif cmd.upper().startswith("MOUNT"):
            parts = cmd.split()
            if len(parts) > 1:
                vol = parts[1].lower()
                valid_vols = {
                    "ntfs": "oeneye-ntfs.img",
                    "sufficient": "oeneye-sufficient-v2.img",
                    "fat32": "oeneye-mosfetq-fat32.img"
                }
                if vol in valid_vols:
                    print(f"Successfully mounted active virtual volume: {valid_vols[vol]}")
                else:
                    print(f"Unknown volume. Available targets: {list(valid_vols.keys())}")
            else:
                print("Usage: MOUNT [ntfs | sufficient | fat32]")
"""

if 'elif cmd.upper().startswith("OENEYECUDA"):' in code:
    code = code.replace('elif cmd.upper().startswith("OENEYECUDA"):', mount_command + '\n        elif cmd.upper().startswith("OENEYECUDA"):')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added MOUNT command handler to MOSFETQ-DOS v18.0!")
else:
    print("Could not locate OENEYECUDA hook.")
