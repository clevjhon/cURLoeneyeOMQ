import subprocess

commands = [
    b"ver\r",
    b"mem\r",
    b"dir\r",
    b"type readme.txt\r"
]

for cmd in commands:
    print(f"--- Running: {cmd.decode().strip()} ---")
    result = subprocess.run(
        ["python3", "emu.py", cmd],
        capture_output=True,
        text=True
    )
    print(result.stdout)
