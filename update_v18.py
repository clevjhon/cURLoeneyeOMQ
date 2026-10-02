with open("emu_dos.py", "r") as f:
    code = f.read()

# Update version string banner from MOSFETQ DOS to v18.0
old_banner = "MOSFETQ-DOS Compact MOSFETQ DOS (oeneye Trace Edition)"
new_banner = "MOSFETQ-DOS Compact v18.0 (oeneye SDK v1.0.0 Integrated Edition)"

if old_banner in code:
    code = code.replace(old_banner, new_banner)
    with open("emu_dos.py", "w") as f:
        f.write(code)
    print("Successfully updated emulator banner to MOSFETQ-DOS v18.0!")
else:
    print("Could not locate MOSFETQ DOS banner string in emu_dos.py.")
        
