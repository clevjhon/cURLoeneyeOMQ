with open("emu.py", "r") as f:
    code = f.read()

target = 'elif cmd.upper().startswith("MOUNT"):'

dir_block = """
        elif cmd.upper().startswith("DIR"):
            import os
            free_space = 104857600000
            print(" Volume in drive A has no label.")
            print(" Directory of A:\\\\")
            print()
            files = [
                "oeneye-ntfs.img",
                "oeneye-sufficient-v2.img",
                "oeneye-mosfetq-fat32.img"
            ]
            total_bytes = 0
            for f_name in files:
                if os.path.exists(f_name):
                    f_size = os.path.getsize(f_name)
                    total_bytes += f_size
                    print(f"  {f_name:<26} {f_size:>10,d} bytes")
                else:
                    print(f"  {f_name:<26} [Not Found]")
            print(f"               3 File(s) {total_bytes:>12,d} bytes")
            print(f"               0 Dir(s)  {free_space:,} bytes free")
        elif cmd.upper().startswith("MOUNT"):
"""

if target in code and "DIR" not in code:
    code = code.replace(target, dir_block)
    with open("emu.py", "w") as f:
        f.write(code)
    print("Forced insertion of DIR command successful!")
else:
    print("Target already contains DIR or MOUNT hook not found.")
