with open("emu_dos.py", "r") as f:
    code = f.read()

import re

# Remove any existing custom command blocks to start clean
code = re.sub(r'[ \t]*elif cmd == "COPY":.*?(?=\n[ \t]*elif|\n[ \t]*else:)', '', code, flags=re.DOTALL)
code = re.sub(r'[ \t]*elif cmd == "READSECTOR":.*?(?=\n[ \t]*elif|\n[ \t]*else:)', '', code, flags=re.DOTALL)
code = re.sub(r'[ \t]*elif cmd == "IRC":.*?(?=\n[ \t]*elif|\n[ \t]*else:)', '', code, flags=re.DOTALL)
code = re.sub(r'[ \t]*elif cmd in \("HASH", "CHECKSUM"\):.*?(?=\n[ \t]*elif|\n[ \t]*else:)', '', code, flags=re.DOTALL)

handlers = """    elif cmd == "COPY":
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

    elif cmd in ("HASH", "CHECKSUM"):
        target_file = arg.strip() if arg else "oeneye.iso"
        if os.path.exists(target_file):
            sha256_hash = hashlib.sha256()
            md5_hash = hashlib.md5()
            with open(target_file, "rb") as f_obj:
                for byte_block in iter(lambda: f_obj.read(4096), b""):
                    sha256_hash.update(byte_block)
                    md5_hash.update(byte_block)
            print(f"File: {target_file}")
            print(f" MD5:    {md5_hash.hexdigest()}")
            print(f" SHA256: {sha256_hash.hexdigest()}")
        else:
            print(f"File not found: {target_file}")

    elif cmd == "IRC":
        print("[oeneyeIRC] Initializing secure socket connection...")
        print("[oeneyeIRC] Connected to network backbone (simulated).")
        print("[oeneyeIRC] Type /QUIT to return to oeneyeOS prompt.")
        while True:
            try:
                irc_input = input("[oeneyeIRC]> ").strip()
                if irc_input.upper() == "/QUIT":
                    print("[oeneyeIRC] Disconnected from session.")
                    break
                elif irc_input.upper().startswith("/JOIN "):
                    ch = irc_input.split()[1]
                    print(f"[oeneyeIRC] Joined channel: {ch}")
                else:
                    print(f"[oeneyeIRC] Message sent: {irc_input}")
            except (KeyboardInterrupt, EOFError):
                print("\\n[oeneyeIRC] Session terminated.")
                break
"""

target = '    else:\n        print("Bad command or file name")'
if target not in code:
    target = 'else:\n        print("Bad command or file name")'

if target in code:
    code = code.replace(target, handlers + "\n    " + target, 1)
    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("[SUCCESS] emu_dos.py sanitized and handlers re-inserted cleanly.")
else:
    print("[ERROR] Fallback else block not found.")
