import os
import subprocess
import hashlib

print("Downloading oeneye-mosfetq-fat32.img from Zenodo archive...")
url = "https://zenodo.org/records/22983037/files/oeneye-mosfetq-fat32.img?download=1"
output_filename = "oeneye-mosfetq-fat32.img"

try:
    subprocess.run(["curl", "-L", url, "-o", output_filename], check=True)
    size = os.path.getsize(output_filename)
    print(f"Successfully downloaded {output_filename} ({size} bytes).")
    
    # Compute SHA-256 for integrity verification
    sha256_hash = hashlib.sha256()
    with open(output_filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    print(f"SHA-256 Digest: {sha256_hash.hexdigest()}")
except subprocess.CalledProcessError as e:
    print(f"Failed to download image via curl: {e}")
