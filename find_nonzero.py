with open("oeneye-00x00.img", "rb") as f:
    data = f.read()
    
for i, b in enumerate(data):
    if b != 0:
        print(f"First non-zero byte found at offset {i} (0x{i:x}): 0x{b:02x}")
        break
else:
    print("The entire file consists solely of null bytes (0x00).")
