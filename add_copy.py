with open("emu_dos.py", "r") as f:
    code = f.read()

copy_handler = """    elif cmd == "COPY":
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

"""

target = '    else:\n        print("Bad command or file name")'
if 'elif cmd == "COPY":' not in code and target in code:
    code = code.replace(target, copy_handler + target, 1)
    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("[SUCCESS] COPY command handler added.")
else:
    print("[INFO] COPY command handler already exists or target not found.")
