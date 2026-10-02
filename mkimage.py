#!/usr/bin/env python3
"""Build mosfetq-dos.img: boot sector + kernel + FAT12 volume with sample files."""
import struct, sys

bin_ = open("mosfetq-dos.bin", "rb").read()
boot, kernel = bin_[:512], bin_[512:]
assert boot[510:512] == b"\x55\xaa", "boot signature missing"

# --- read the BPB the assembler emitted, and lay the volume out from it ---
bps, spc, rsv, nfat, rootent, tot16, media, fatsz, spt, heads = struct.unpack_from("<HBHBHHBHHH", boot, 0x0B)
assert (bps, spc, nfat, rootent, tot16, fatsz, spt, heads) == (512, 1, 2, 224, 2880, 9, 18, 2)
assert len(kernel) <= (rsv - 1) * bps, f"kernel {len(kernel)} B does not fit in {rsv-1} sectors"
fat_lba  = rsv
root_lba = fat_lba + nfat * fatsz
root_sec = rootent * 32 // bps
data_lba = root_lba + root_sec
assert (fat_lba, root_lba, root_sec, data_lba) == (17, 35, 14, 49), "update .equ constants in the .s file"

img = bytearray(tot16 * bps)
img[0:512] = boot
img[512:512 + len(kernel)] = kernel

# --- FAT12 helpers ---
fat = {0: 0xFF0, 1: 0xFFF}
next_free = [2]
def alloc():
    c = next_free[0]; next_free[0] += 1; return c
def write_cluster(c, data):
    off = (data_lba + c - 2) * bps
    img[off:off + bps] = data.ljust(bps, b"\0")

def store(chunks):
    """chunks: list of cluster-sized byte blocks already allocated -> chain"""
    pass

files = {}   # name -> (first_cluster, size)
def make_name(n):
    base, _, ext = n.upper().partition(".")
    return base.ljust(8).encode() + ext.ljust(3).encode()

def add_files(spec):
    """spec: list of (name, data). Clusters are handed out round-robin so that
    files that are listed together end up interleaved (fragmented)."""
    chains = {n: [] for n, _ in spec}
    blocks = {n: [d[i:i + bps] for i in range(0, max(len(d), 1), bps)] for n, d in spec}
    while any(blocks.values()):
        for n, _ in spec:
            if blocks[n]:
                c = alloc(); chains[n].append(c)
                write_cluster(c, blocks[n].pop(0))
    for n, d in spec:
        ch = chains[n]
        for a, b in zip(ch, ch[1:]): fat[a] = b
        fat[ch[-1]] = 0xFFF
        files[n] = (ch[0], len(d), ch)

readme = (b"MOSFETQ DOS 0.2 reads this file from a real FAT12 volume.\r\n"
          b"The kernel walks the FAT cluster chain itself.\n")   # mixed CRLF / LF
hello  = b"Hello from the disk!\r\n"
long_  = b"".join(b"Line %03d: the quick brown fox jumps over the lazy dog.\r\n" % i for i in range(1, 41))
frag   = b"".join(b"FRAG %03d ---------------------------------------------\r\n" % i for i in range(1, 51))
pad    = bytes(range(33, 127)) * 40                              # interleaves with FRAG.TXT
add_files([("README.TXT", readme), ("HELLO.TXT", hello), ("LONG.TXT", long_)])
add_files([("FRAG.TXT", frag), ("PAD.BIN", pad)])
big = b"".join(b"BIG %05d ==========================================\r\n" % i for i in range(1, 1346))[:70000]
add_files([("BIG.TXT", big)])

# a directory (cluster with '.' and '..') so DIR shows <DIR>
dir_c = alloc(); fat[dir_c] = 0xFFF
def dirent(name11, attr, cluster, size):
    return name11 + bytes([attr]) + bytes(10) + struct.pack("<HHHI", 0, 0x4C21, cluster, size)
write_cluster(dir_c, dirent(b".".ljust(11), 0x10, dir_c, 0) + dirent(b"..".ljust(11), 0x10, 0, 0))

# --- root directory ---
root = bytearray()
root += dirent(b"MOSFETQ    ", 0x08, 0, 0)                        # volume label (DIR must hide it)
root += dirent(b"\xE5OLD    TXT", 0x20, 2, 10)                    # deleted entry (DIR must hide it)
for n, (c, s, _) in files.items():
    root += dirent(make_name(n), 0x20, c, s)
root += dirent(b"DOCS       ", 0x10, dir_c, 0)
img[root_lba * bps: root_lba * bps + len(root)] = root

# --- FAT12 packing (two copies) ---
fat_bytes = bytearray(fatsz * bps)
for n, v in fat.items():
    o = n + n // 2
    w = fat_bytes[o] | (fat_bytes[o + 1] << 8)
    w = (w & 0xF000) | v if n % 2 == 0 else (w & 0x000F) | (v << 4)
    fat_bytes[o], fat_bytes[o + 1] = w & 0xFF, w >> 8
for i in range(nfat):
    o = (fat_lba + i * fatsz) * bps
    img[o:o + len(fat_bytes)] = fat_bytes

open("mosfetq-dos.img", "wb").write(img)
print(f"kernel {len(kernel)} of {(rsv-1)*bps} bytes; {len(files)} files + DOCS/; image {len(img)} bytes")
for n, (c, s, ch) in files.items(): print(f"  {n:11s} {s:5d} B  clusters {ch}")

# --- Include OMQ.FNT from local assets ---
try:
    with open("assets/fonts/OMQ.FNT", "rb") as ff:
        font_bytes = ff.read()
    # Add to files list for FAT12 injection
    files["OMQ.FNT"] = (0, len(font_bytes), font_bytes) # Note: handled via custom layout or add_files
except FileNotFoundError:
    print("Warning: assets/fonts/OMQ.FNT not found, skipping build injection.")
