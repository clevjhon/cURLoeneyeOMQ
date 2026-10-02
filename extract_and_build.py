import os

with open('oeneye-mosfetq-fat16.img', 'rb') as f:
    b = f.read(512)
    res = int.from_bytes(b[14:16], 'little')
    fc = b[16]
    spf = int.from_bytes(b[22:24], 'little')
    re = int.from_bytes(b[17:19], 'little')
    rds = res + (fc * spf)
    ds = rds + ((re * 32 + 511) // 512)
    
    f.seek(512 * rds)
    for i in range(re):
        e = f.read(32)
        if not e or e[0] in (0, 229): continue
        attr = e[11]
        if attr & 0x08 or attr & 0x10: continue # Skip volume label and subdirs
        name = e[0:8].decode('ascii', 'ignore').strip().lower()
        ext = e[8:11].decode('ascii', 'ignore').strip().lower()
        filename = f"{name}.{ext}" if ext else name
        
        cluster = int.from_bytes(e[26:28], 'little')
        size = int.from_bytes(e[28:32], 'little')
        
        pos = f.tell()
        f.seek(512 * (ds + cluster - 2))
        data = f.read(size)
        with open(filename, 'wb') as out:
            out.write(data)
        print(f"Extracted: {filename} ({size} bytes)")
        f.seek(pos)
