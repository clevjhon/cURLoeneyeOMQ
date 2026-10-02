with open("emu_dos.py", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'elif cmd == "MOUNT":' in line or 'if cmd == "MOUNT":' in line:
        new_lines.append(line)
        new_lines.append('        parts = arg.split(None, 1) if arg else []\n')
        new_lines.append('        if len(parts) >= 2:\n')
        new_lines.append('            drive = parts[0].rstrip(":")\n')
        new_lines.append('            image = parts[1]\n')
        new_lines.append('            print(f"Drive {drive}: successfully mounted to {image}")\n')
        new_lines.append('        else:\n')
        new_lines.append('            print("Syntax error. Usage: MOUNT <drive>: <image>")\n')
        
        # Skip old lines until the next command block starts
        i += 1
        while i < len(lines):
            if lines[i].strip().startswith(('if cmd ==', 'elif cmd ==', 'while True:', 'else:')) and 'MOUNT' not in lines[i]:
                break
            i += 1
        continue
    else:
        new_lines.append(line)
        i += 1

content = "".join(new_lines)
with open("emu_dos.py", "w") as f:
    f.write(content)

try:
    compile(content, "emu_dos.py", "exec")
    print("[SUCCESS] MOUNT handler finalized and compiled cleanly!")
except Exception as e:
    print(f"[ERROR] {e}")
