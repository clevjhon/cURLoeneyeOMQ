with open("emu.py", "r") as f:
    lines = f.readlines()

if len(lines) >= 284:
    idx = 283  # 0-indexed for line 284
    if not lines[idx].strip().startswith("#"):
        lines[idx] = "# " + lines[idx]

with open("emu.py", "w") as f:
    f.writelines(lines)

print("Line 284 neutralized!")
