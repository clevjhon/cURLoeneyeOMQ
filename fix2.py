with open("emu.py", "r") as f:
    lines = f.readlines()

for i in range(215, min(240, len(lines))):
    if not lines[i].strip().startswith("#"):
        lines[i] = "# " + lines[i]

with open("emu.py", "w") as f:
    f.writelines(lines)

print("Troubled region commented out successfully!")
