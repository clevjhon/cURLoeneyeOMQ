import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   REFS FILE SYSTEM ROOT INSPECTION")
print("========================================")

refs_offset = 0x0003
fsrs_offset = 0x0010

# Read ReFS header block (64 bytes)
refs_chunk = data[refs_offset:refs_offset + 64]
print(f"\n[+] ReFS Root Header at 0x{refs_offset:04X}:")
hex_str = " ".join(f"{b:02X}" for b in refs_chunk[:32])
print(f"    Bytes: {hex_str}")

# Read FSRS header block (64 bytes)
fsrs_chunk = data[fsrs_offset:fsrs_offset + 64]
print(f"\n[+] FSRS Reference Structure at 0x{fsrs_offset:04X}:")
hex_str = " ".join(f"{b:02X}" for b in fsrs_chunk[:32])
print(f"    Bytes: {hex_str}")

print("\n========================================")
print("Inspection Complete.")
