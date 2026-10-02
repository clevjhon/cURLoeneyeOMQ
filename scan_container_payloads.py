import struct

with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

print("========================================")
print("   GLOBAL CONTAINER PAYLOAD SCANNER")
print("========================================")

chunk_size = 512
total_size = len(data)
active_chunks = []

# Scan the entire file in 512-byte blocks
for offset in range(0, total_size, chunk_size):
    block = data[offset : offset + chunk_size]
    # Check if the block is not entirely zero
    if any(b != 0 for b in block):
        # Grab first 4 bytes for magic/signature inspection
        sig = block[0:4]
        active_chunks.append((offset, sig))

print(f"[*] Found {len(active_chunks)} non-zero blocks out of {total_size // chunk_size} total blocks.")
print("\n[+] Active Blocks Summary (Sample):")
for offset, sig in active_chunks[:15]:  # Show first 15 active blocks
    # Try to decode ASCII representation if possible
    try:
        ascii_sig = sig.decode('ascii')
        if not ascii_sig.isalnum():
            ascii_sig = " ".join(f"{b:02X}" for b in sig)
    except:
        ascii_sig = " ".join(f"{b:02X}" for b in sig)
        
    print(f"    - Offset 0x{offset:05X}: Signature/Prefix -> {ascii_sig}")

print("\n========================================")
print("Scan Complete.")
