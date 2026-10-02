import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   CHKP CHECKPOINT TABLE PARSER")
print("========================================")

chkp_offset = 0x28000
chunk = data[chkp_offset : chkp_offset + 64]

magic = chunk[0:4]
print(f"[*] Checkpoint Magic : {magic.decode('ascii', errors='ignore')} (Hex: {magic.hex()})")

# Unpack delta transaction table slots following the header
slots = struct.unpack("<IIIIIIII", chunk[4:36])

for i, slot in enumerate(slots):
    print(f"    - Transaction Slot [{i}] (Offset +{4 + (i*4)}): 0x{slot:08X} ({slot})")

print("\n========================================")
print("Parsing Complete.")
