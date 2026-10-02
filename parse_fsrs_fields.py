import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   FSRS DESCRIPTOR FIELD UNPACKER")
print("========================================")

fsrs_offset = 0x0010
chunk = data[fsrs_offset : fsrs_offset + 32]

# Magic header (4 bytes)
magic = chunk[0:4]

# Unpack following fields (assuming standard 32-bit and 16-bit integers)
# Let us inspect the raw slice using different formats
print(f"Magic Header : {magic.decode('latin1', errors='ignore')}")

# Unpack integers starting right after magic bytes (offset +4)
# Let's read a sequence of 32-bit integers
values = struct.unpack("<IIIIIII", chunk[4:32])

for i, val in enumerate(values):
    print(f"    - Field [{i}] (Offset +{4 + (i*4)}): 0x{val:08X} ({val})")

print("\n========================================")
print("Unpacking Complete.")
