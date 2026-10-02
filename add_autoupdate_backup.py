with open("emu_dos.py", "r") as f:
    code = f.read()

# 1. Add auto-update check at startup inside main()
startup_hook = """    # Auto-update workspace/repo check
    import subprocess
    print("Checking for repository updates...")
    try:
        subprocess.run(["git", "pull"], capture_output=True, text=True, timeout=3)
    except Exception:
        pass
"""

if "Loading MOSFETQ DOS..." in code and "git pull" not in code:
    code = code.replace('print("Loading MOSFETQ DOS...")', 'print("Loading MOSFETQ DOS...")\n' + startup_hook)

# 2. Add auto-backup trigger upon exiting the emulator (e.g. on EXIT command)
exit_backup_hook = """    if os.path.exists("backup.py"):
        print("Running automatic session backup...")
        subprocess.run(["python3", "backup.py"], capture_output=True, text=True)
"""

if 'cmd == "EXIT"' in code and "automatic session backup" not in code:
    code = code.replace('elif cmd == "EXIT":', exit_backup_hook + '    elif cmd == "EXIT":')

with open("emu_dos.py", "w") as f:
    f.write(code)

print("Auto-update and auto-backup hooks injected!")
