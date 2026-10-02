import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   OENEYE KERNEL PAYLOAD EXTRACTOR")
print("========================================")

# Based on our FSRS capacity and 512-byte block stride
block_size = 512
base_offset = 0x0010

# Scan the first few blocks for payload markers or pointer offsets
for i in range(10):
    node_offset = base_offset + (i * block_size)
    chunk = data[node_offset : node_offset + 32]
    
    magic = chunk[0:4]
    print(f"[*] Block [{i}] at 0x{node_offset:04X}: Magic -> {magic}")
    
    # Check if there are embedded size or pointer fields in the next 28 bytes
    pointers = struct.unpack("<IIIIIII", chunk[4:32])
    # Filter for non-zero interesting offsets/sizes
    active_ptrs = [p for p in pointers if p > 0]
    if active_ptrs:
        print(f"    - Non-zero descriptors: {[hex(p) for p in active_ptrs]}")

print("\n========================================")
print("Scan Complete.")
