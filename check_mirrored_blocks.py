import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   MIRRORED BACKUP BLOCK INSPECTION")
print("========================================")

backup_offset = 0xC7E03
print(f"\n[*] Inspecting backup block region near 0x{backup_offset:05X}:")

if backup_offset + 64 <= len(data):
    chunk = data[backup_offset : backup_offset + 64]
    hex_str = " ".join(f"{b:02X}" for b in chunk[:32])
    print(f"    Bytes: {hex_str}")
    
    # Check for known magic signatures
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"    ASCII: {ascii_str[:32]}")
else:
    print("    [!] Warning: Backup offset exceeds file size.")

print("\n========================================")
print("Inspection Complete.")
