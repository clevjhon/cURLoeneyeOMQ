import os
import datetime

SUPB_SIGNATURE = b'\xD8\xC3\xB2\xA5' # 0xA5B2C3D8 in little-endian representation
LOG_FILE = "oeneye_audit.log"

def log_audit(message):
    timestamp = datetime.datetime.now().isoformat()
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def verify_files():
    log_audit("START: Initiating oeneye high-assurance audit sweep.")
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f != "oeneye_verify.py" and f != "search_zenodo.py" and f != "download_zenodo.py"]
    
    total_files = len(files)
    passed = 0

    log_audit(f"Found {total_files} target asset(s) for verification.")

    for filename in files:
        size = os.path.getsize(filename)
        # Check 512-byte block alignment requirement
        is_aligned = (size % 512 == 0)
        
        # Check signature if it's a binary image
        has_supb = False
        if filename.endswith('.img') or filename.endswith('.bin'):
            with open(filename, 'rb') as f:
                header = f.read(512)
                if SUPB_SIGNATURE in header:
                    has_supb = True

        status = "PASS" if is_aligned else "WARN (Unaligned size)"
        if is_aligned:
            passed += 1

        log_audit(f"FILE: {filename} | Size: {size} bytes | 512-Aligned: {is_aligned} | SUPB Found: {has_supb} | Status: {status}")

    log_audit(f"SUMMARY: Verified {total_files} files. {passed}/{total_files} met strict 512-byte block alignment.")
    log_audit("END: Audit sequence completed successfully.")

if __name__ == "__main__":
    verify_files()
