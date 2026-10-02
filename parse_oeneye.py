with open("oeneye-bootstrap.img", "rb") as f:
    data = f.read()

tags = {
    b"ReFS": "Primary File System Root",
    b"FSRS": "File System Reference Structure",
    b"SUPB": "Superblock Configuration",
    b"CHKP": "Transaction Checkpoint State"
}

print("========================================")
print("   OENEYE BOOTSTRAP PARSER UTILITY")
print("========================================")

for tag, description in tags.items():
    pos = 0
    while True:
        idx = data.find(tag, pos)
        if idx == -1:
            break
        checksum_idx = data.find(b"\xD8\xC3\xB2\xA5", idx, idx + 64)
        sig_status = f"Valid (Offset 0x{checksum_idx:04X})" if checksum_idx != -1 else "Not Found"
        print(f"\n[+] Found {tag.decode()} ({description})")
        print(f"    - Offset       : 0x{idx:04X} ({idx})")
        print(f"    - Checksum Sig : {sig_status}")
        pos = idx + len(tag)

print("\n========================================")
print("Parsing Complete.")
