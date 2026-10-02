import struct

def extract_container_data(filename):
    with open(filename, "rb") as f:
        data = f.read()

    print("========================================")
    print("   OENEYE CONTAINER EXTRACTION UTILITY")
    print("========================================")

    # 1. Extract Superblock Payload Regions
    supb_offset = 0x1E000
    print(f"\n[*] Extracting Superblock at 0x{supb_offset:04X}")
    supb_data = data[supb_offset:supb_offset + 512]
    with open("supb_dump.bin", "wb") as out:
        out.write(supb_data)
    print("    -> Saved 512 bytes to supb_dump.bin")

    # 2. Extract Checkpoint State Regions & Delta Table Targets
    chkp_offset = 0x28000
    print(f"\n[*] Extracting Checkpoint at 0x{chkp_offset:04X}")
    chkp_data = data[chkp_offset:chkp_offset + 512]
    with open("chkp_dump.bin", "wb") as out:
        out.write(chkp_data)
    print("    -> Saved 512 bytes to chkp_dump.bin")

    # 3. Read Transaction Delta Table offsets inside CHKP and extract referenced slices
    delta_base = chkp_offset + 0x90
    print("\n[*] Extracting Delta/Transaction Slices:")
    for i in range(4):
        chunk = data[delta_base + (i*4) : delta_base + (i*4) + 4]
        val = struct.unpack("<I", chunk)[0]
        
        # Calculate target sector/offset based on delta value
        target_offset = chkp_offset + val
        if target_offset < len(data):
            slice_data = data[target_offset:target_offset + 64]
            slice_filename = f"delta_slice_{i}_off_{val:04X}.bin"
            with open(slice_filename, "wb") as out:
                out.write(slice_data)
            print(f"    -> Slice [{i}] (Delta: {val}): Saved 64 bytes to {slice_filename}")

    print("\n========================================")
    print("Extraction Complete.")

if __name__ == "__main__":
    extract_container_data("oeneye-bootstrap.img")
