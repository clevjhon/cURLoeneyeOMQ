with open("emu.py", "r") as f:
    code = f.read()

if "MOSFETQ-DOS" not in code and "A:\\" not in code:
    startup_code = '''
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
    except (KeyboardInterrupt, EOFError):
        break
'''
    code += startup_code
    with open("emu.py", "w") as f:
        f.write(code)
    print("Startup loop appended successfully!")
else:
    print("Startup loop already present.")
