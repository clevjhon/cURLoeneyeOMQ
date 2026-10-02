import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   OENEYE DEEP POINTER TRAVERSAL")
print("========================================")

# Locate Superblock SUPB at 0x1E000
supb_offset = 0x1E000
if data[supb_offset:supb_offset+4] == b"SUPB":
    print(f"\n[+] Inspecting Superblock (SUPB) at 0x{supb_offset:04X}")
    
    # Read pointer region around 0x1E0C0 (where CHKP offsets were found)
    pointer_region_offset = supb_offset + 0xC0
    raw_pointers = data[pointer_region_offset:pointer_region_offset+8]
    
    # Unpack two 32-bit integer pointers
    ptr1, ptr2 = struct.unpack("<II", raw_pointers)
    print(f"    - Target Checkpoint Pointer 1 : 0x{ptr1:04X} ({ptr1})")
    print(f"    - Target Checkpoint Pointer 2 : 0x{ptr2:04X} ({ptr2})")

# Locate Checkpoint CHKP at 0x28000
chkp_offset = 0x28000
if data[chkp_offset:chkp_offset+4] == b"CHKP":
    print(f"\n[+] Inspecting Checkpoint (CHKP) at 0x{chkp_offset:04X}")
    
    # Read transaction delta table starting at offset +0x90 within the block
    delta_base = chkp_offset + 0x90
    print("    - First 4 Delta/Transaction Offsets:")
    for i in range(4):
        chunk = data[delta_base + (i*4) : delta_base + (i*4) + 4]
        val = struct.unpack("<I", chunk)[0]
        print(f"      [{i}] Value: 0x{val:08X} ({val})")

print("\n========================================")
print("Traversal Complete.")
