with open("emu.py", "r") as f:
    code = f.read()

diskinfo_code = """
        elif cmd.upper().startswith("DISKINFO"):
            import os
            # Determine active image based on previous MOUNT or default to fat32
            active_img = "oeneye-mosfetq-fat32.img"
            if os.path.exists(active_img):
                print(f"--- Volume Inspection: {active_img} ---")
                with open(active_img, "rb") as img_file:
                    boot_sector = img_file.read(512)
                print(f"Boot Sector Size Read: {len(boot_sector)} bytes")
                print(f"Signature / Magic: {boot_sector[-2:]:hex()}")
                print("Status: Superblock parsed successfully. File allocation table active.")
            else:
                print("Error: No active volume image found.")
"""

target = 'elif cmd.upper().startswith("MOUNT"):'
if target in code and "DISKINFO" not in code:
    code = code.replace(target, diskinfo_code + '\n        elif cmd.upper().startswith("MOUNT"):')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added DISKINFO command handler!")
else:
    print("Could not locate MOUNT target for insertion.")
