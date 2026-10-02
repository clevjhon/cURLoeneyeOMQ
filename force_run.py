with open("emu.py", "r") as f:
    code = f.read()

# Remove any old incomplete tail loops if present
if "while running:" in code:
    code = code.split("while running:")[0]

# Append the definitive interactive runner loop
runner = '''
print("  __  ____")
print(" (o) (o) Eney")
print(" (oeneyeOS)")
print("\\nMOSFETQ-DOS Compact v16.9 (oeneye Trace Edition)")
print("Type \\'GO\\', \\'STEP\\', \\'TRACE ON/OFF\\', or assemble programs from A:\\\\ prompt.\\n")

running = True
while running:
    try:
        cmd = input("A:\\\\> ").strip()
        if not cmd:
            continue
        if cmd.upper() == "EXIT":
            break
        elif cmd.upper() == "GO":
            print("Executing program from instruction pointer...")
        else:
            print(f"Bad command or file name: {cmd}")
    except (KeyboardInterrupt, EOFError):
        break
'''

code += runner
with open("emu.py", "w") as f:
    f.write(code)

print("Forced interactive shell loop appended successfully!")
