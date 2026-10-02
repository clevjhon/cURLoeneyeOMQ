with open("emu_dos.py", "r") as f:
    lines = f.readlines()

# Let's inspect lines around 50-70 and filter out the duplicate block
new_lines = []
skip = False
for idx, line in enumerate(lines):
    # If we hit the duplicate redundant else block for mount around line 61
    if 59 <= idx <= 64 and "else:" in line and "LS" not in lines[idx+5]:
        skip = True
        continue
    if skip and (idx <= 64):
        continue
    else:
        skip = False
        new_lines.append(line)

content = "".join(new_lines)
with open("emu_dos.py", "w") as f:
    f.write(content)

try:
    compile(content, "emu_dos.py", "exec")
    print("[SUCCESS] Duplicate MOUNT block removed and compiled cleanly!")
except Exception as e:
    print(f"[ERROR] {e}")
