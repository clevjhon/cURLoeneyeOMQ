with open("emu.py", "r") as f:
    lines = f.readlines()

for i in range(139, min(156, len(lines))):
    print(f"{i+1:3d}: {repr(lines[i])}")
