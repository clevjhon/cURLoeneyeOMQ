import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   FSRS NODE MAPPING UTILITY")
print("========================================")

# Parameters from FSRS analysis
block_size = 512
capacity = 1600
base_offset = 0x0010

print(f"[*] Scanning file system nodes using {block_size}-byte strides...")
active_nodes = []

# Scan through potential node slots based on capacity and stride
for i in range(20):  # Inspecting the first 20 nodes as a sample block
    node_offset = base_offset + (i * block_size)
    if node_offset + 16 > len(data):
        break
    
    chunk = data[node_offset : node_offset + 16]
    magic_or_flag = struct.unpack("<I", chunk[0:4])[0]
    
    # Check if slot contains non-zero data
    if magic_or_flag != 0:
        active_nodes.append((i, node_offset, magic_or_flag))
        print(f"    [+] Active Node [{i}] at Offset 0x{node_offset:04X}: Header/Flag = 0x{magic_or_flag:08X}")

print(f"\nFound {len(active_nodes)} active nodes in initial sample sweep.")
print("========================================")
print("Mapping Complete.")
