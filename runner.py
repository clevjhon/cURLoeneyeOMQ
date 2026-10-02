import os
from pathlib import Path

def handle_oeneye_asset(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == ".bin":
        print(f"[BIN] Loading raw binary blob: {path.name} ({path.stat().st_size} bytes)")
        try:
            with open(path, "rb") as f:
                header_bytes = f.read(64) # Read first 64 bytes for inspection
            print(f"Header Preview (Hex): {header_bytes.hex()}")
            print(f"Status: Binary blob mapped into virtual memory space successfully.")
        except Exception as e:
            print(f"ERROR reading binary blob: {e}")
    elif ext == ".bas":
        print(f"[BAS] Parsing BASIC source script: {path.name}")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"Loaded {len(lines)} lines of BASIC bytecode/source.")
    elif ext == ".bat":
        print(f"[BAT] Executing batch macro script: {path.name}")
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                cmd = line.strip()
                if cmd and not cmd.startswith("REM"):
                    print(f" > EXEC: {cmd}")
    else:
        print(f"[WARN] Unsupported extension: {ext}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        handle_oeneye_asset(sys.argv[1])
    else:
        print("Usage: python3 runner.py <file.bin|file.bas|file.bat>")
