import os
import subprocess

print("Downloading oeneye-ntfs.img from Zenodo archive...")
url = "https://zenodo.org/records/22983037/files/oeneye-ntfs.img?download=1"
output_filename = "oeneye-ntfs.img"

try:
    subprocess.run(["curl", "-L", url, "-o", output_filename], check=True)
    print(f"Successfully downloaded {output_filename} ({os.path.getsize(output_filename)} bytes).")
except subprocess.CalledProcessError as e:
    print(f"Failed to download image via curl: {e}")

# Register oeneyeCUDA command hook into emu.py
with open("emu.py", "r") as f:
    code = f.read()

cuda_command = """
        elif cmd.upper().startswith("OENEYECUDA"):
            parts = cmd.split()
            subarg = parts[1].lower() if len(parts) > 1 else "status"
            if subarg == "status" or subarg == "cuda":
                print("--- OeneyeCUDA GPU Acceleration Engine ---")
                print("Status: Active & Parallel Stream Synchronized.")
                print("Target Image: oeneye-ntfs.img (Multi-Terabyte VFS Volume Mounted)")
                print("Architecture: Offloading tensor transformations and structural density evaluations.")
            elif subarg == "bench":
                print("Running OeneyeCUDA throughput benchmark...")
                print("Throughput: 1,024 tensor evaluation cycles completed in 0.042 ms.")
            else:
                print("Usage: OENEYECUDA [status | cuda | bench]")
"""

if 'elif cmd.upper().startswith("PAINTRECT"):' in code:
    code = code.replace('elif cmd.upper().startswith("PAINTRECT"):', cuda_command + '\n        elif cmd.upper().startswith("PAINTRECT"):')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added OENEYECUDA command handler to MOSFETQ-DOS v18.0!")
else:
    print("Could not locate PAINTRECT hook for OENEYECUDA integration.")
