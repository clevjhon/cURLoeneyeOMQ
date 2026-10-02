import struct, sys

import time, hashlib, os, platform

_FB_W, _FB_H = 320, 200
_FB = bytearray(_FB_W * _FB_H * 4)

def paint_cmd(cmd):
    parts = cmd.split()
    name = parts[0].upper()
    if name == "PAINTCLEAR":
        color = int(parts[1], 0) if len(parts) > 1 else 0x000000FF
        px = bytes([(color >> 24) & 255, (color >> 16) & 255, (color >> 8) & 255, color & 255])
        _FB[:] = px * (_FB_W * _FB_H)
        print("Clearing 320x200 framebuffer at 0xA000:0000 with color 0x%08X (256,000 bytes reset)." % color)
    elif name == "PAINTRECT":
        try:
            x, y, w, h = (int(p) for p in parts[1:5])
            color = int(parts[5], 0)
        except (ValueError, IndexError):
            print("Usage: PAINTRECT <x> <y> <w> <h> <color_hex>")
            return
        px = bytes([(color >> 24) & 255, (color >> 16) & 255, (color >> 8) & 255, color & 255])
        for yy in range(max(y, 0), min(y + h, _FB_H)):
            for xx in range(max(x, 0), min(x + w, _FB_W)):
                i = (yy * _FB_W + xx) * 4
                _FB[i:i+4] = px
        print("Drawing rectangle at (%d,%d) with size %dx%d and color 0x%08X." % (x, y, w, h, color))
    elif name == "PAINTVIEW":
        shades = " .:-=+*#%@"
        cols, rows = 64, 32
        for r in range(rows):
            line = []
            for c in range(cols):
                i = ((r * _FB_H // rows) * _FB_W + (c * _FB_W // cols)) * 4
                b = (_FB[i] + _FB[i+1] + _FB[i+2]) / 765.0
                line.append(shades[int(b * (len(shades) - 1))])
            print("".join(line))
    elif name == "PAINTSAVE":
        path = parts[1] if len(parts) > 1 else "framebuffer.ppm"
        with open(path, "wb") as out:
            out.write(("P6\n%d %d\n255\n" % (_FB_W, _FB_H)).encode())
            out.write(b"".join(bytes(_FB[i:i+3]) for i in range(0, len(_FB), 4)))
        print("Framebuffer written to %s (%dx%d PPM)." % (path, _FB_W, _FB_H))


def oeneyecuda_cmd(cmd):
    parts = cmd.split()
    sub = parts[1].lower() if len(parts) > 1 else "help"
    img = "oeneye-ntfs.img"
    if sub == "bench":
        n = 48
        a = [[(i * j) % 7 + 1 for j in range(n)] for i in range(n)]
        b = [[(i + j) % 5 + 1 for j in range(n)] for i in range(n)]
        t0 = time.perf_counter()
    h = hashlib.sha256()
    size = 0
    if os.path.exists(img):
        with open(img, "rb") as f:
            while True:
                chunk = f.read(1 << 20)
                if not chunk:
                    break
                h.update(chunk)
                size += len(chunk)
        dt = time.perf_counter() - t0
        print(f"SHA-256 of {img}: {size:,} bytes in {dt*1000:.1f} ms ({size/dt/1e6:.1f} MB/s)")
        print(f"Digest: {h.hexdigest()[:32]}...")
    else:
        print(f"{img} not found - skipped hash benchmark.")
    




# Interactive MOSFETQ-DOS REPL Loop with Auto-Mount and Multi-Mount Support
import os

valid_vols = {
    "fat12": "fat12.img",
    "fat16": "fat16.img",
    "upscaled": "upscaled.img",
    "dosnt": "DOSoeneyeNT.img",
    "ntdos": "NToeneyeDOS.img",
    "dos1440": "mosfetq-dos-1440.img",
    "dos1200": "mosfetq-dos-1200.img"
}

if "env_state" not in globals():
    env_state = {"active_idx": 2,"mounted": []}
elif "mounted" not in env_state:
    env_state["mounted"] = []

# Automatically mount all available volume files present on disk
print("Scanning and auto-mounting available volumes...")
for vkey, vfile in valid_vols.items():
    if os.path.exists(vfile):
        if vfile not in env_state["mounted"]:
            env_state["mounted"].append(vfile)
        print(f"  [Auto-Mounted] {vkey} -> {vfile}")

while True:
    try:
        cmd = input("MOSFETQ-DOS> ").strip()
        if not cmd:
            continue
        if cmd.upper() == "EXIT":
            break
        elif cmd.upper() in ["AUTOMOUNT", "MOUNT ALL"]:
            count = 0
            for vkey, vfile in valid_vols.items():
                if os.path.exists(vfile) and vfile not in env_state["mounted"]:
                    env_state["mounted"].append(vfile)
                    count += 1
                    print(f"Auto-mounted: {vkey} -> {vfile}")
            print(f"Automount complete. Total newly mounted: {count}. Active mounts: {len(env_state["mounted"])}")
        elif cmd.upper().startswith("MOUNT"):
            parts = cmd.split()
            if len(parts) > 1:
                v = parts[1].lower()
                if v in valid_vols:
                    img_file = valid_vols[v]
                    if os.path.exists(img_file):
                        if img_file not in env_state["mounted"]:
                            env_state["mounted"].append(img_file)
                        print(f"Mounted volume [{v}]: {img_file}. Total active mounts: {len(env_state["mounted"])}")
                    else:
                        print(f"Error: Image file {img_file} not found on disk.")
                else:
                    print("Unknown volume. Available: " + ", ".join(valid_vols.keys()))
            else:
                print("Currently mounted volumes: " + ", ".join(env_state["mounted"]) if env_state["mounted"] else "None")
        elif cmd.upper() == "DISKINFO":
            print("Active Mounted Volumes:")
            for idx, m in enumerate(env_state.get("mounted", [])):
                print(f"  Drive {chr(65+idx)}: {m}")
            if not env_state.get("mounted"):
                print("  None")
        
        elif cmd.upper().startswith("DUMP"):
            parts = cmd.split()
            mounted = env_state.get("mounted", [])
            if not mounted:
                print("No volumes mounted.")
            else:
                target = mounted[0]
                if len(parts) > 1:
                    arg = parts[1].upper()
                    if len(arg) == 1 and arg in "ABCD":
                        idx = ord(arg) - ord("A")
                        if idx < len(mounted):
                            target = mounted[idx]
                        else:
                            print(f"Drive {arg} is not active.")
                            target = None
                    else:
                        for m in mounted:
                            if arg.lower() in m.lower():
                                target = m
                                break
                if target and os.path.exists(target):
                    print(f"--- Boot Sector Preview (First 64 bytes) of {target} ---")
                    with open(target, "rb") as bf:
                        data = bf.read(64)
                        hex_chunks = " ".join(f"{b:02X}" for b in data)
                        ascii_repr = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
                        print("HEX:  ", hex_chunks[:47])
                        print("      ", hex_chunks[47:95])
                        print("ASCII:", ascii_repr)
                elif target:
                    print(f"Target container {target} not found.")
    
        
        elif cmd.upper().startswith("TOUCH"):
            parts = cmd.split()
            if len(parts) > 1:
                fname = parts[1]
                mounted = env_state.get("mounted", [])
                if not mounted:
                    print("No volumes mounted.")
                else:
                    target = mounted[0]
                    try:
                        with open(target, "r+b") as bf:
                            bf.seek(11)
                            bps = int.from_bytes(bf.read(2), "little")
                            rsvd = int.from_bytes(bf.read(2), "little")
                            num_fats = bf.read(1)[0]
                            root_entries = int.from_bytes(bf.read(2), "little")
                            bf.seek(22)
                            spf = int.from_bytes(bf.read(2), "little")
                            
                            root_dir_offset = (rsvd + (num_fats * spf)) * bps
                            root_dir_size = root_entries * 32
                            
                            fn_parts = fname.split(".")
                            base = fn_parts[0][:8].upper().ljust(8, " ")
                            ext = fn_parts[1][:3].upper().ljust(3, " ") if len(fn_parts) > 1 else "   "
                            
                            bf.seek(root_dir_offset)
                            root_data = bytearray(bf.read(root_dir_size))
                            
                            written = False
                            for i in range(0, len(root_data), 32):
                                if root_data[i] == 0x00 or root_data[i] == 0xE5:
                                    entry = bytearray(32)
                                    entry[0:8] = base.encode("ascii")
                                    entry[8:11] = ext.encode("ascii")
                                    entry[11] = 0x20 # Archive attribute
                                    entry[26:28] = (2).to_bytes(2, "little") # Cluster 2
                                    entry[28:32] = (128).to_bytes(4, "little") # 128 bytes size
                                    
                                    root_data[i:i+32] = entry
                                    bf.seek(root_dir_offset)
                                    bf.write(root_data)
                                    print(f"File {base.strip()}.{ext.strip()} created successfully in {target}!")
                                    written = True
                                    break
#                             if not written:
# 
# 
# 
#         except:
#             pass
#             pass
#             parts = cmd.split()
            if len(parts) > 1:
                target_file = parts[1].upper()
                mounted = env_state.get("mounted", [])
                if not mounted:
                    print("No volumes mounted.")
                else:
                    target = mounted[0]
                    try:
                        with open(target, "rb") as bf:
                            bf.seek(11)
                            bps = int.from_bytes(bf.read(2), "little")
                            rsvd = int.from_bytes(bf.read(2), "little")
                            num_fats = bf.read(1)[0]
                            root_entries = int.from_bytes(bf.read(2), "little")
                            bf.seek(13)
                            spc = bf.read(1)[0]
                            bf.seek(22)
                            spf = int.from_bytes(bf.read(2), "little")
                            
                            root_dir_offset = (rsvd + (num_fats * spf)) * bps
                            root_dir_size = root_entries * 32
                            
                            bf.seek(root_dir_offset)
                            root_data = bf.read(root_dir_size)
                            
                            found = False
                            for i in range(0, len(root_data), 32):
                                entry = root_data[i:i+32]
                                if entry[0] == 0x00:
                                    break
                                if entry[0] in (0xE5, 0x05) or (entry[11] & 0x08) or entry[11] == 0x0F:
                                    continue
                                name = entry[0:8].decode("ascii", errors="ignore").strip()
                                ext = entry[8:11].decode("ascii", errors="ignore").strip()
                                fullname = f"{name}.{ext}" if ext else name
                                if fullname == target_file:
                                    cluster = int.from_bytes(entry[26:28], "little")
                                    size = int.from_bytes(entry[28:32], "little")
                                    
                                    root_dir_sectors = (root_dir_size + bps - 1) // bps
                                    first_data_sector = rsvd + (num_fats * spf) + root_dir_sectors
                                    cluster_offset = (first_data_sector + (cluster - 2) * spc) * bps
                                    
                                    bf.seek(cluster_offset)
                                    read_size = size if size > 0 else 128
                                    content = bf.read(read_size)
                                    print(f"--- Contents of {fullname} ---")
                                    print(content.decode("ascii", errors="replace").rstrip("\x00"))
                                    found = True
                                    break
                            if not found:
                                print(f"File not found: {target_file}")
        except Exception as e:
                        print(f"Error reading file: {e}")
            else:
                print("Usage: TYPE <FILENAME.EXT>")

        
        elif cmd.upper().startswith("WRITE"):
            parts = cmd.split(maxsplit=2)
            if len(parts) >= 3:
                target_file = parts[1].upper()
                content_str = parts[2] + "\n"
                mounted = env_state.get("mounted", [])
                if not mounted:
                    print("No volumes mounted.")
                else:
                    target = mounted[0]
                    try:
                        with open(target, "r+b") as bf:
                            bf.seek(11)
                            bps = int.from_bytes(bf.read(2), "little")
                            rsvd = int.from_bytes(bf.read(2), "little")
                            num_fats = bf.read(1)[0]
                            root_entries = int.from_bytes(bf.read(2), "little")
                            bf.seek(13)
                            spc = bf.read(1)[0]
                            bf.seek(22)
                            spf = int.from_bytes(bf.read(2), "little")
                            
                            root_dir_offset = (rsvd + (num_fats * spf)) * bps
                            root_dir_size = root_entries * 32
                            
                            bf.seek(root_dir_offset)
                            root_data = bytearray(bf.read(root_dir_size))
                            
                            found = False
                            for i in range(0, len(root_data), 32):
                                entry = root_data[i:i+32]
                                if entry[0] == 0x00:
                                    break
                                if entry[0] in (0xE5, 0x05) or (entry[11] & 0x08) or entry[11] == 0x0F:
                                    continue
                                name = entry[0:8].decode("ascii", errors="ignore").strip()
                                ext = entry[8:11].decode("ascii", errors="ignore").strip()
                                fullname = f"{name}.{ext}" if ext else name
                                if fullname == target_file:
                                    cluster = int.from_bytes(entry[26:28], "little")
                                    
                                    root_dir_sectors = (root_dir_size + bps - 1) // bps
                                    first_data_sector = rsvd + (num_fats * spf) + root_dir_sectors
                                    cluster_offset = (first_data_sector + (cluster - 2) * spc) * bps
                                    
                                    bf.seek(cluster_offset)
                                    payload = content_str.encode("ascii", errors="ignore")
                                    bf.write(payload)
                                    
                                    # Update file size in directory entry
                                    entry[28:32] = len(payload).to_bytes(4, "little")
                                    root_data[i:i+32] = entry
                                    bf.seek(root_dir_offset)
                                    bf.write(root_data)
                                    
                                    print(f"Successfully wrote {len(payload)} bytes to {target_file}!")
                                    found = True
                                    break
                            if not found:
                                print(f"File not found: {target_file}. Use TOUCH first.")
        except Exception as e:
                        print(f"Error writing to file: {e}")
            else:
                print("Usage: WRITE <FILENAME.EXT> <TEXT>")

        
        elif cmd.upper().startswith("DEL"):
            parts = cmd.split()
            if len(parts) > 1:
                target_file = parts[1].upper()
                mounted = env_state.get("mounted", [])
                if not mounted:
                    print("No volumes mounted.")
                else:
                    target = mounted[0]
                    try:
                        with open(target, "r+b") as bf:
                            bf.seek(11)
                            bps = int.from_bytes(bf.read(2), "little")
                            rsvd = int.from_bytes(bf.read(2), "little")
                            num_fats = bf.read(1)[0]
                            root_entries = int.from_bytes(bf.read(2), "little")
                            bf.seek(22)
                            spf = int.from_bytes(bf.read(2), "little")
                            
                            root_dir_offset = (rsvd + (num_fats * spf)) * bps
                            root_dir_size = root_entries * 32
                            
                            bf.seek(root_dir_offset)
                            root_data = bytearray(bf.read(root_dir_size))
                            
                            found = False
                            for i in range(0, len(root_data), 32):
                                entry = root_data[i:i+32]
                                if entry[0] == 0x00:
                                    break
                                if entry[0] in (0xE5, 0x05) or (entry[11] & 0x08) or entry[11] == 0x0F:
                                    continue
                                name = entry[0:8].decode("ascii", errors="ignore").strip()
                                ext = entry[8:11].decode("ascii", errors="ignore").strip()
                                fullname = f"{name}.{ext}" if ext else name
                                if fullname == target_file:
                                    root_data[i] = 0xE5
                                    bf.seek(root_dir_offset)
                                    bf.write(root_data)
                                    print(f"File {target_file} deleted successfully from {target}!")
                                    found = True
                                    break
                            if not found:
                                print(f"File not found: {target_file}")
        except Exception as e:
                        print(f"Error deleting file: {e}")
            else:
                print("Usage: DEL <FILENAME.EXT>")

        elif cmd.upper().strip() in ["A:", "B:", "C:", "D:"]:
            dmap = {"A:": 0, "B:": 1, "C:": 2, "D:": 3}
            idx = dmap[cmd.upper().strip()]
            mounted = env_state.get("mounted", [])
            if idx < len(mounted):
                env_state["active_idx"] = idx
                print(f"Current drive changed to {cmd.upper().strip()} -> {mounted[idx]}")
            else:
                print(f"Drive {cmd.upper().strip()} is not mounted.")
        elif cmd.upper() == "DIR":
            mounted = env_state.get("mounted", [])
            if not mounted:
                print("No volumes mounted.")
            else:
                m = mounted[act_idx]
                print(f"--- Directory of Drive {dletter}: ({m}) ---")
        try:
                        with open(m, "rb") as bf:
                            bf.seek(11)
                            bps = int.from_bytes(bf.read(2), "little")
                            rsvd = int.from_bytes(bf.read(2), "little")
                            num_fats = bf.read(1)[0]
                            root_entries = int.from_bytes(bf.read(2), "little")
                            bf.seek(22)
                            spf = int.from_bytes(bf.read(2), "little")
                            
                            root_dir_offset = (rsvd + (num_fats * spf)) * bps
                            root_dir_size = root_entries * 32
                            
                            bf.seek(root_dir_offset)
                            root_data = bf.read(root_dir_size)
                            
                            files_found = 0
                            for i in range(0, len(root_data), 32):
                                entry = root_data[i:i+32]
                                first_byte = entry[0]
                                if first_byte == 0x00:
                                    break
                                if first_byte == 0xE5 or first_byte == 0x05:
                                    continue
                                attr = entry[11]
                                if attr & 0x08 or attr == 0x0F:
                                    continue
                                name = entry[0:8].decode("ascii", errors="ignore").strip()
                                ext = entry[8:11].decode("ascii", errors="ignore").strip()
                                size = int.from_bytes(entry[28:32], "little")
                                if name:
                                    fullname = f"{name}.{ext}" if ext else name
                                    print(f"  {fullname:<12} {size:>8} bytes")
                                    files_found += 1
                            if files_found == 0:
                                print("  (Empty root directory)")
        except Exception as e:
                        print(f"  Error parsing FAT structure: {e}")
        else:
            print("Unknown command: " + cmd)
    except (KeyboardInterrupt, EOFError):
        break
