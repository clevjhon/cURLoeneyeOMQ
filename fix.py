with open("emu.py", "r") as f:
    lines = f.readlines()

for i in range(min(215, len(lines)), min(240, len(lines))):
    if lines[i].strip() in ("try:", "except:", "except Exception as e:"):
        lines[i] = "# " + lines[i]

with open("emu.py", "w") as f:
    f.writelines(lines)

print("Problematic try/except lines neutralized!")
