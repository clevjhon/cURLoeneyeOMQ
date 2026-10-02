import os
import struct
import sys
from emu_dos import get_disk_geometry, main as dos_main, print_banner

def oeneye_boot_sequence():
    print("[*] Initializing oeneye.exe x86 runtime container...")
    print("[*] Loading symbolic operator engine and autopoietic memory spaces...")
    
    image_path = "mosfetq-dos.img"
    if not os.path.exists(image_path):
        print("[-] Error: Volume image missing. Run setup first.")
        return False
    
    with open(image_path, "rb") as f:
        geo = get_disk_geometry(f)
        print(f"[+] Volume mounted successfully.")
        print(f"    - Sector Size: {geo['bytes_per_sec']} bytes")
        print(f"    - FAT Count: {geo['num_fats']}")
        print(f"    - Root Entries: {geo['root_entries']}")
        print(f"    - Data Start Sector: {geo['data_start_sec']}")

    print("\n[+] oeneye.exe kernel link established. Handing over to MOSFETQ DOS shell...\n")
    return True

if __name__ == "__main__":
    if oeneye_boot_sequence():
        dos_main()
