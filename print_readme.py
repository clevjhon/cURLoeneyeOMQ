f = open('oeneye-mosfetq-fat16.img', 'rb')
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
    if 'README' in e[0:11].decode('ascii', 'ignore'):
        cluster = int.from_bytes(e[26:28], 'little')
        size = int.from_bytes(e[28:32], 'little')
        f.seek(512 * (ds + cluster - 2))
        print(f.read(size).decode('ascii', 'ignore'))
