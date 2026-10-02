import os
import sys
import subprocess
import shutil
import datetime
import glob
import platform

def get_system_stamping():
    try:
        uname = os.uname()
        kernel_info = f"Linux Kernel {uname.release}"
    except Exception:
        kernel_info = f"Linux {platform.release()}"
    
    # Check if running under Termux/Android
    is_android = os.path.exists("/system/build.prop") or "termux" in os.environ.get("PREFIX", "").lower()
    
    if is_android:
        return f"Powered by Android ({kernel_info} - ARM64)"
    else:
        return f"Powered by {kernel_info} (ARM64)"

def get_all_drive_mappings():
    boot_img = "oeneye-bootstrap.img"
    if not os.path.exists(boot_img):
        boot_img = "floppy_img.bin"

    mappings = {
        "A": boot_img,
        "C": ".",
        "W": "workspace",
        "X": "shared_storage"
    }

    files = sorted(glob.glob("*.img") + glob.glob("*.zip") + glob.glob("*.tar*") + glob.glob("*.gz"))
    available_letters = [chr(c) for c in range(ord('D'), ord('Z')+1) if chr(c) not in mappings]
    
    for f_path, letter in zip(files, available_letters):
        mappings[letter] = f_path
    return mappings

DRIVE_MAPPINGS = get_all_drive_mappings()

def run_backup():
    if os.path.exists("backup.py"):
        print("Running automatic session backup...")
        subprocess.run(["python3", "backup.py"], capture_output=True, text=True)

def main():
    global current_path, current_drive
    current_path = "A:\\"
    
    print("Checking for repository updates...")
    try:
        subprocess.run(["git", "pull"], capture_output=True, text=True, timeout=3)
    except Exception:
        pass

    print("Loading MOSFETQ DOS v20...")
    print(f"\n{get_system_stamping()}")
    print("MOSFETQ DOS v20.0 Runtime Core")
    print("Subsystem anchored to oeneye v0.2 Floppy Kernel Architecture (Pinned & Locked)")
    print("Type HELP for a list of commands.")



def cmd_dir(img_data):
    # Parse FAT12 Root Directory (Sector 19 on standard floppy / or offset calculation)
    # FAT12 boot sector is usually 512 bytes, 2 FATs of 9 sectors = 18 sectors -> Root dir starts at sector 19 (offset 19 * 512 = 9728)
    root_offset = 19 * 512
    root_entries = 224 # standard 1.44MB floppy root entries
    print(" Volume in drive A has no label.")
    print(" Directory of A:\\\n")
    
    count = 0
    total_bytes = 0
    for i in range(root_entries):
        entry_offset = root_offset + (i * 32)
        if entry_offset + 32 > len(img_data):
            break
        entry = img_data[entry_offset:entry_offset+32]
        first_byte = entry[0]
        
        if first_byte == 0x00:
            break # Unused entries marker
        if first_byte == 0xE5:
            continue # Deleted entry
        
        attr = entry[11]
        if attr == 0x0F:
            continue # Skip LFN entries
            
        name_bytes = entry[0:8]
        ext_bytes = entry[8:11]
        
        # Check if it is a volume label
        if attr & 0x08:
            continue
            
        name = name_bytes.decode("ascii", errors="ignore").strip()
        ext = ext_bytes.decode("ascii", errors="ignore").strip()
        
        filename = f"{name}.{ext}" if ext else name
        
        # File size is at offset 28-31 (4 bytes)
        file_size = int.from_bytes(entry[28:32], byteorder="little")
        
        is_dir = (attr & 0x10) != 0
        
        if is_dir:
            print(f"{filename:<12} <DIR>")
        else:
            print(f"{filename:<12} {file_size:>10} bytes")
            count += 1
            total_bytes += file_size

    print(f"\n       {count} File(s) {total_bytes} bytes free\n")

current_drive = "A"
while True:
    try:
        prompt_str = current_drive + ":\\> "
        line = input(prompt_str)
        if not line.strip():
            continue
        parts = line.strip().split()
        cmd = parts[0].upper()
        if cmd == "EXIT":
            print("Exiting emulator.")
            break
        elif cmd == "HELP":
            print("Available commands: DIR, TREE, MAP, CD <dir>, CLS, EXIT, BACKUP, oeneyeMOUNT, oeneyeUNMOUNT")
        elif cmd == "MAP":
            print("Active Drive Mappings (v20 Core / v0.2 Floppy Backed):")
            for drv, path in DRIVE_MAPPINGS.items():
                if os.path.exists(path):
                    print(f"  {drv} -> {path}")
        elif cmd == "DIR":
            target_img = DRIVE_MAPPINGS.get(current_drive, "oeneye.img")
            try:
                with open(target_img, "rb") as f_img:
                    img_data = f_img.read()
                cmd_dir(img_data)
            except Exception as e:
                print(f"Error reading drive image: {e}")
        elif cmd == "OENEYEMOUNT":
            print("Mounting oeneyeOS subsystem and updating image loops...")
            # Placeholder for mount logic
        elif cmd == "OENEYEUNMOUNT":
            print("Unmounting oeneyeOS subsystem safely...")
            # Placeholder for unmount logic
        
        elif cmd == "MOUNT":
            # Usage: MOUNT <drive>: <filename.ximg>
            if len(parts) >= 3:
                target_drv = parts[1].rstrip(":").upper()
                img_file = parts[2]
                if target_drv in DRIVE_MAPPINGS:
                    DRIVE_MAPPINGS[target_drv] = img_file
                    print(f"Drive {target_drv}: successfully mounted to {img_file}")
                else:
                    print(f"Invalid drive specifier: {target_drv}")
                print("Syntax error. Usage: MOUNT <drive>: <image>")
        elif cmd == "UNMOUNT":
            if len(parts) >= 2:
                target_drv = parts[1].rstrip(":").upper()
                if target_drv in DRIVE_MAPPINGS:
                    DRIVE_MAPPINGS[target_drv] = ""
                    print(f"Drive {target_drv}: unmounted.")
                else:
                    print(f"Invalid drive specifier: {target_drv}")
                print("Syntax error. Usage: UNMOUNT <drive>:")

    except (KeyboardInterrupt, EOFError):
        break
