with open("emu_dos.py", "r") as f:
    content = f.read()

lines = content.splitlines()
new_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    if 'elif cmd == "IRC":' in line or 'if cmd == "IRC":' in line:
        new_lines.append(line)
        new_lines.append('        print("[oeneyeIRC] Initializing secure socket connection...")')
        new_lines.append('        print("[oeneyeIRC] Connected to network backbone (simulated).")')
        new_lines.append('        print("[oeneyeIRC] Type /QUIT to return to oeneyeOS prompt.")')
        new_lines.append('        while True:')
        new_lines.append('            try:')
        new_lines.append('                irc_input = input("[oeneyeIRC]> ").strip()')
        new_lines.append('                if irc_input.upper() == "/QUIT":')
        new_lines.append('                    print("[oeneyeIRC] Disconnected from session.")')
        new_lines.append('                    break')
        new_lines.append('                elif irc_input.upper().startswith("/JOIN "):')
        new_lines.append('                    ch = irc_input.split()[1]')
        new_lines.append('                    print(f"[oeneyeIRC] Joined channel {ch}")')
        new_lines.append('                else:')
        new_lines.append('                    print(f"[oeneyeIRC Broadcast] {irc_input}")')
        new_lines.append('            except (KeyboardInterrupt, EOFError):')
        new_lines.append('                print("\\n[oeneyeIRC] Session terminated.")')
        new_lines.append('                break')
        
        # Skip until the end of the file or next main command handler
        i += 1
        while i < len(lines):
            if lines[i].strip().startswith(('if cmd ==', 'elif cmd ==', 'while True:')) and 'IRC' not in lines[i]:
                break
            i += 1
        continue
    else:
        new_lines.append(line)
        i += 1

cleaned = "\n".join(new_lines) + "\n"
with open("emu_dos.py", "w") as f:
    f.write(cleaned)

try:
    compile(cleaned, "emu_dos.py", "exec")
    print("[SUCCESS] emu_dos.py compiled cleanly and perfectly!")
except Exception as e:
    print(f"[ERROR] {e}")
