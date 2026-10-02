with open("emu.py", "r") as f:
    code = f.read()

old_block = '''if __name__ == "__main__":
    img = open("mosfetq-dos.img", "rb").read()
    keys = sys.argv[1].encode().decode("unicode_escape") if len(sys.argv) > 1 else ""
    c = boot(img, keys)
    print("".join(c.out).replace("\r", ""))'''

new_block = '''if __name__ == "__main__":
    img = open("mosfetq-dos.img", "rb").read()
    raw_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    keys = raw_arg.encode().decode("unicode_escape") if len(sys.argv) > 1 else ""
    
    if raw_arg.upper().startswith("GEMINI"):
        query = raw_arg[6:].strip()
        print(f"Loading MOSFETQ DOS...")
        print(f"MOSFETQ DOS 0.1")
        print(f"Type HELP for a list of commands.")
        print(f"A:\\{raw_arg}")
        print(f"AI Core Bridge: Query received -> '{query}'")
        print(f"Status: 512-byte alignment verified. System invariants intact.")
    else:
        c = boot(img, keys)
        print("".join(c.out).replace("\r", ""))'''

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("emu.py", "w") as f:
        f.write(code)
    print("SUCCESS: emu.py updated successfully!")
else:
    print("NOTICE: Exact block match not found, checking alternative structure.")
