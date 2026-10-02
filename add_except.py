with open("emu_dos.py", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    new_lines.append(line)
    if 'try:' in line and i+1 < len(lines) and 'irc_input' in lines[i+1]:
        # Find where to insert except:
        pass
    i += 1

# Let's write a targeted fix for the IRC try/except block
content = "".join(lines)
if "try:" in content and "except:" not in content:
    # Insert except: before the loop ends or after input
    content = content.replace(
        '            if irc_input.upper() == "/QUIT":\n                print("[oeneyeIRC] Disconnected from session.")\n                break',
        '            if irc_input.upper() == "/QUIT":\n                print("[oeneyeIRC] Disconnected from session.")\n                break\n        except:\n            break'
    )

with open("emu_dos.py", "w") as f:
    f.write(content)

try:
    compile(content, "emu_dos.py", "exec")
    print("[SUCCESS] emu_dos.py compiled successfully!")
except Exception as e:
    print(f"[ERROR] {e}")
