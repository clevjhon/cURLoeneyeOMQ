import subprocess
import urllib.request

# 1. Download v0.2 image if not already present
url = "https://zenodo.org/records/22845198/files/mosfetq-dos.img?download=1"
print("Downloading MOSFETQ DOS v0.2...")
urllib.request.urlretrieve(url, "mosfetq-dos.img")

# 2. Define test commands (expanding on v0.1 tests)
commands = [
    b"ver\r",
    b"mem\r",
    b"dir\r",
    b"type readme.txt\r",
    b"type todo.txt\r",
    b"cd DOCS\r",
    b"dir\r"
]

# 3. Execute commands via emulator
for cmd in commands:
    print(f"\n--- Running: {cmd.decode().strip()} ---")
    result = subprocess.run(
        ["python3", "emu.py", cmd],
        capture_output=True,
        text=True
    )
    print(result.stdout)
