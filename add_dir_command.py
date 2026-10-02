with open("emu.py", "r") as f:
    code = f.read()

dir_command = """
        elif cmd.upper() == "DIR" or cmd.upper().startswith("DIR "):
            import os
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
"""

# Inject free_space variable definition if not present or handle it gracefully
free_space_var = "free_space = 104857600000\n"

if 'elif cmd.upper().startswith("MOUNT"):' in code:
    code = code.replace('elif cmd.upper().startswith("MOUNT"):', free_space_var + '\n' + dir_command + '\n        elif cmd.upper().startswith("MOUNT"):')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added DIR command handler to MOSFETQ-DOS v18.0!")
else:
    print("Could not locate MOUNT hook.")
