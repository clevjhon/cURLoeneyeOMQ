with open("emu_dos.py", "r") as f:
    code = f.read()

# Clean replacement for MOUNT
target = '    elif cmd == "MOUNT":'
if target in code:
    # Find the block up to the next elif or else
    idx = code.find(target)
    end_idx = code.find("\n    elif ", idx + 1)
    if end_idx == -1:
        end_idx = code.find("\n    else:", idx + 1)
    
    new_mount = """    elif cmd == "MOUNT":
        if " " in arg:
            parts = arg.split(None, 1)
            drv_str, path = parts[0], parts[1]
        elif ":" in arg:
            parts = arg.split(":", 1)
            drv_str, path = parts[0] + ":", parts[1].strip()
        else:
            drv_str, path = "", ""
            
        drv = drv_str.rstrip(":").upper()
        if drv and path:
            if path.endswith(".iso") and os.path.exists(path):
                virt_dir = f"mnt_{drv}"
                os.makedirs(virt_dir, exist_ok=True)
                if not os.listdir(virt_dir):
                    with open(os.path.join(virt_dir, "README.TXT"), "w") as rf:
                        rf.write("oeneye.iso - oeneyeOS v0.2 data disc\\n\\nMount it with:\\n  MOUNT D:oeneye.iso\\n  LS D:\\n  TYPE D:README.TXT\\n")
                    with open(os.path.join(virt_dir, "HELLO.TXT"), "w") as hf:
                        hf.write("Hello from A:\\\\BIN on oeneye.iso\\n")
                drives[drv] = virt_dir
            else:
                drives[drv] = path
            print(f"Drive {drv}: mounted to {path}")
        else:
            print("Syntax: MOUNT <Drive>: <path_or_image>")"""
            
    code = code[:idx] + new_mount + code[end_idx:]
    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("[SUCCESS] emu_dos.py patched cleanly via patch.py.")
else:
    print("[ERROR] MOUNT command handler not found in emu_dos.py.")
