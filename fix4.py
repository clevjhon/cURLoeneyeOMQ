with open("emu.py", "r") as f:
    lines = f.readlines()

if len(lines) >= 286:
    idx = 285  # 0-indexed for line 286
    if not lines[idx].strip().startswith("#"):
        lines[idx] = "# " + lines[idx]

with open("emu.py", "w") as f:
    f.writelines(lines)

print("Line 286 neutralized!")
