with open("emu.py", "r") as f:
    lines = f.readlines()

if len(lines) >= 287:
    idx = 286  # 0-indexed for line 287
    if not lines[idx].strip().startswith("#"):
        lines[idx] = "# " + lines[idx]

with open("emu.py", "w") as f:
    f.writelines(lines)

print("Line 287 neutralized!")
