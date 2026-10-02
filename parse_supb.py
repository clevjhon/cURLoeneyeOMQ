import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   SUPB SUPERBLOCK POINTER PARSER")
print("========================================")

supb_offset = 0x1E000
chunk = data[supb_offset : supb_offset + 64]

magic = chunk[0:4]
print(f"[*] Superblock Magic : {magic.decode('ascii', errors='ignore')}")

# Unpack a sequence of 32-bit integers following the magic header
values = struct.unpack("<IIIIIIII", chunk[4:36])

for i, val in enumerate(values):
    print(f"    - Pointer / Field [{i}] (Offset +{4 + (i*4)}): 0x{val:08X} ({val})")

print("\n========================================")
print("Parsing Complete.")
