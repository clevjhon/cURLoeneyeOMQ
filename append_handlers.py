with open("emu_dos.py", "r") as f:
    code = f.read()

new_block = """    elif cmd == "COPY":
        parts = arg.split(None, 1)
        if len(parts) == 2:
            src, dst = parts[0], parts[1]
            if ":" in src:
                drv, src_path = src.split(":", 1)
                src_path = src_path.lstrip("\\\\/")
                base_path = drives.get(drv.upper(), ".")
                if os.path.isdir(base_path):
                    src = os.path.join(base_path, src_path)
            if ":" in dst:
                drv, dst_path = dst.split(":", 1)
                dst_path = dst_path.lstrip("\\\\/")
                base_path = drives.get(drv.upper(), ".")
                if os.path.isdir(base_path):
                    dst = os.path.join(base_path, dst_path)

            if os.path.exists(src):
                with open(src, "rb") as sf, open(dst, "wb") as df:
                    df.write(sf.read())
                print(f"Successfully copied {src} to {dst}")
            else:
                print(f"Source not found: {src}")
        else:
            print("Syntax: COPY <source> <destination>")

    elif cmd == "READSECTOR":
        parts = arg.split(None, 2)
        if len(parts) >= 1:
            target = parts[0]
            offset = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 128
            if os.path.exists(target):
                with open(target, "rb") as bf:
                    bf.seek(offset)
                    data = bf.read(size)
                    print(f"--- Sector Dump [{target} @ offset {offset}, {size} bytes] ---")
                    print(data)
            else:
                print(f"File not found: {target}")
        else:
            print("Syntax: READSECTOR <image_file> [offset] [size]")
"""

# Insert right before the loop ends or before standard print for bad command
if "elif cmd == \"COPY\":" not in code:
    # Find where input loop handles commands, let's inject before print("Bad command or file name") or similar
    pos = code.rfind("print(")
    if pos != -1:
        # Find the start of that line
        line_start = code.rfind("\n", 0, pos)
        code = code[:line_start] + "\n" + new_block + code[line_start:]
        with open("emu_dos.py", "w") as f:
            f.write(code)
        print("[SUCCESS] Handlers appended successfully.")
    else:
        print("[ERROR] Could not find injection point.")
else:
    print("[INFO] Handlers already present.")
