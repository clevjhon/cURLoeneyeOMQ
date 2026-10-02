import subprocess
import os
import hashlib

urls = {
    "DOSoeneyeNT.img": "https://zenodo.org/records/22958760/files/DOSoeneyeNT.img?download=1",
    "NToeneyeDOS.img": "https://zenodo.org/records/22958760/files/NToeneyeDOS.img?download=1",
    "mosfetq-dos-1440.img": "https://zenodo.org/records/22958760/files/mosfetq-dos-1.0.0.0.0-dev-1440.img?download=1",
    "mosfetq-dos-1200.img": "https://zenodo.org/records/22958760/files/mosfetq-dos-1.0.0.0.0-dev-1200.img?download=1"
}

for fname, url in urls.items():
    print(f"Downloading {fname}...")
    subprocess.run(["curl", "-L", url, "-o", fname], check=True)
    size = os.path.getsize(fname)
    sha = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    print(f"Verified {fname} ({size} bytes) | SHA-256: {sha.hexdigest()[:16]}...")

# Update valid_vols in emu.py
with open("emu.py", "r") as f:
    code = f.read()

new_vols_block = """    "dosnt": "DOSoeneyeNT.img",
                    "ntdos": "NToeneyeDOS.img",
                    "dos1440": "mosfetq-dos-1440.img",
                    "dos1200": "mosfetq-dos-1200.img",
                    """

if "dosnt" not in code:
    code = code.replace("valid_vols = {", "valid_vols = {\n" + new_vols_block)

with open("emu.py", "w") as f:
    f.write(code)

print("All new disk images downloaded and registered successfully!")
