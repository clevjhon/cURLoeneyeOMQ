import os
import sys
import hashlib
import json
import tarfile
from pathlib import Path
from datetime import datetime

AGI_TOKEN = "000b"
SYSTEM_NAME = "oeneyeOS v0.2"

DRIVE_MAPPINGS = {
    "A": "mosfetq-dos-gold-1.0.0.0.1-5.25in-1.2M.ximg"
}

def auto_backup_workspace():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"oeneyeos_backup_{timestamp}.tar.gz"
    try:
        with tarfile.open(archive_name, "w:gz") as tar:
            for p in Path(".").glob("*"):
                if p.name != archive_name and not p.name.endswith(".tar.gz") and p.name != "emu_dos.py":
                    tar.add(p)
        print(f"[AUTOEXEC] Auto-backup successful: {archive_name}")
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")

def run_checksums():
    manifest = {}
    for p in Path(".").rglob("*"):
        if p.is_file() and not p.name.endswith(".tar.gz") and p.name != "emu_dos.py":
            sha = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha.update(chunk)
            manifest[str(p)] = {"size": p.stat().st_size, "sha256": sha.hexdigest()}
    with open("oeneye_manifest.json", "w") as mf:
        json.dump(manifest, mf, indent=4)
    print(f"[AUTOEXEC] Manifest synchronized: {len(manifest)} files verified and indexed.")

def run_autoexec():
    print("Executing AUTOEXEC.BAT...")
    print("PATH A:\\;A:\\BIN")
    print("SET OS=oeneyeOS")
    print(f"SET AGI_TOKEN={AGI_TOKEN}")
    auto_backup_workspace()
    run_checksums()
    print("[BOOT] AUTOEXEC.BAT completed successfully.\n")

def load_rc():
    if os.path.exists("oeneye.rc"):
        print(f"[BOOT] Loading oeneye.rc configuration...")
        with open("oeneye.rc", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("@") and not line.startswith("REM"):
                    print(f"C> {line}")
        print(f"[BOOT] {SYSTEM_NAME} initialized with AGI Token: {AGI_TOKEN}\n")

def handle_asset(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return

    if ext == ".bin":
        print(f"[BIN] Loading raw binary blob: {path.name} ({path.stat().st_size} bytes)")
        with open(path, "rb") as f:
            header = f.read(64)
        print(f"Header Hex: {header.hex()}")
    elif ext == ".bas":
        print(f"[BAS] Parsing BASIC source script: {path.name}")
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()
        print(f"Loaded {len(lines)} lines of BASIC source/bytecode.")
    elif ext == ".bat":
        print(f"[BAT] Executing batch macro: {path.name}")
        with open(path, "r", errors="ignore") as f:
            for l in f:
                l_str = l.strip()
                if l_str and not l_str.startswith("REM"):
                    print(f" > {l_str}")
    else:
        print(f"[RUNNER] Generic execution handler dispatched for {path.name}")

def main_loop():
    load_rc()
    run_autoexec()
    
    current_drive = "A"
    while True:
        try:
            cmd_line = input(f"{current_drive}:\\> ").strip()
            if not cmd_line:
                continue
                
            parts = cmd_line.split(" ", 1)
            cmd = parts[0].upper()
            args = parts[1] if len(parts) > 1 else ""
            
            if cmd == "EXIT":
                print("Performing final backup before shutdown...")
                auto_backup_workspace()
                print("Exiting oeneyeOS DOS Emulator...")
                break
            elif cmd == "VER":
                print(f"{SYSTEM_NAME} [Version 0.2.000b]")
            elif cmd == "DIR":
                print(" Directory of " + current_drive + ":\\")
                for k, v in DRIVE_MAPPINGS.items():
                    print(f" [IMG] Drive {k}: -> {v}")
                for file in Path(".").glob("*.*"):
                    print(f"       {file.name}  ({file.stat().st_size} bytes)")
            elif cmd == "BACKUP":
                auto_backup_workspace()
            elif cmd == "UPDATE":
                run_checksums()
            elif cmd == "RUN" and args:
                handle_asset(args)
            elif cmd == "INT48":
                print(f"[INT 48h TELEMETRY] AGI Token Active: {AGI_TOKEN} | Quadrant: Q2 (Blue)")
            else:
                print(f"Bad command or file name: {cmd}")
        except KeyboardInterrupt:
            print("\nUse EXIT to quit emulator.")

if __name__ == "__main__":
    main_loop()
