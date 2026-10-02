with open("emu_dos.py", "r") as f:
    code = f.read()

# Ensure hashlib is imported
if "import hashlib" not in code:
    code = "import hashlib\n" + code

target = '    elif cmd == "MOUNT":'
new_handler = '''    elif cmd in ("HASH", "CHECKSUM"):
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

    elif cmd == "MOUNT":'''

if target in code and 'elif cmd in ("HASH", "CHECKSUM")' not in code:
    code = code.replace(target, new_handler, 1)
    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("[SUCCESS] Checksum command added successfully.")
else:
    print("[INFO] Checksum command already exists or target not found.")
