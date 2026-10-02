with open("emu_dos.py", "r") as f:
    for idx, line in enumerate(f):
        if "while " in line or "cmd" in line:
            print(f"Line {idx+1}: {line.strip()}")
