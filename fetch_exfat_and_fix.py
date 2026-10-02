import os
import subprocess
import hashlib

print("Downloading oeneye-mosfetq-exfat.img from Zenodo archive...")
url = "https://zenodo.org/records/22983037/files/oeneye-mosfetq-exfat.img?download=1"
output_filename = "oeneye-mosfetq-exfat.img"

try:
    subprocess.run(["curl", "-L", url, "-o", output_filename], check=True)
    size = os.path.getsize(output_filename)
    print(f"Successfully downloaded {output_filename} ({size} bytes).")
    
    sha256_hash = hashlib.sha256()
    with open(output_filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    print(f"SHA-256 Digest: {sha256_hash.hexdigest()}")
except subprocess.CalledProcessError as e:
    print(f"Failed to download image via curl: {e}")

# Now patch emu.py: fix DISKINFO hex formatting and add exfat support
with open("emu.py", "r") as f:
    code = f.read()

# Fix DISKINFO bytes.hex() syntax error
code = code.replace("boot_sector[-2:]:hex()", "boot_sector[-2:].hex()")

# Add exfat to MOUNT dictionary if not already there
if '"exfat"' not in code:
    code = code.replace(
        '"fat32": "oeneye-mosfetq-fat32.img"',
        '"fat32": "oeneye-mosfetq-fat32.img",\n                    "exfat": "oeneye-mosfetq-exfat.img"'
    )

# Add exfat to DIR files list if not already there
if 'oeneye-mosfetq-exfat.img' not in code and 'oeneye-mosfetq-fat32.img' in code:
    code = code.replace(
        '"oeneye-mosfetq-fat32.img"',
        '"oeneye-mosfetq-fat32.img",\n                "oeneye-mosfetq-exfat.img"'
    )

with open("emu.py", "w") as f:
    f.write(code)

print("Patched emu.py successfully!")
