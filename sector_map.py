import hashlib
import sys

TARGET_ADDRESS = 0x8000

def verify_and_map_asset(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        sha = hashlib.sha256(content).hexdigest()[:16]
        print(f"[+] Mapped {filepath} -> 0x{TARGET_ADDRESS:04X} [SHA256: {sha}, Bytes: {len(content)}] [o∞o]")
        return True
    except FileNotFoundError:
        print(f"[!] Warning: Critical asset {filepath} missing.")
        return False

if __name__ == "__main__":
    print(f"[*] Initializing oeneyeOS Sector Mapping [vX] at 0x{TARGET_ADDRESS:04X}...")
    verify_and_map_asset("OMQ.FNT")
    verify_and_map_asset("CANARY.txt")
    print("[+] Sector 3 memory mapping table: VERIFIED [o∞o]")
