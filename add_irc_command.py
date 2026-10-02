with open("emu_dos.py", "r") as f:
    code = f.read()

irc_handler = """    elif cmd == "IRC":
        print("[oeneyeIRC] Initializing secure socket connection...")
        print("[oeneyeIRC] Connected to network backbone (simulated).")
        print("[oeneyeIRC] Type /QUIT to return to oeneyeOS prompt.")
        while True:
            try:
                irc_input = input("[oeneyeIRC]> ").strip()
                if irc_input.upper() == "/QUIT":
                    print("[oeneyeIRC] Disconnected from session.")
                    break
                elif irc_input.upper().startswith("/JOIN "):
                    ch = irc_input.split()[1]
                    print(f"[oeneyeIRC] Joined channel: {ch}")
                else:
                    print(f"[oeneyeIRC] Message sent: {irc_input}")
            except (KeyboardInterrupt, EOFError):
                print("\\n[oeneyeIRC] Session terminated.")
                break
"""

if 'elif cmd == "IRC":' not in code:
    pos = code.rfind("print(")
    if pos != -1:
        line_start = code.rfind("\n", 0, pos)
        code = code[:line_start] + "\n" + irc_handler + code[line_start:]
        with open("emu_dos.py", "w") as f:
            f.write(code)
        print("[SUCCESS] oeneyeIRC command integrated into emu_dos.py.")
    else:
        print("[ERROR] Injection point not found.")
else:
    print("[INFO] oeneyeIRC command already present.")
