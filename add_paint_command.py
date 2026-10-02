with open("emu.py", "r") as f:
    code = f.read()

paint_command = """
        elif cmd.upper() == "OENEYEPAINT":
            print("--- oeneyePaint Raster Graphics Engine ---")
            print("Allocating direct memory-mapped pixel buffer (320x200 RGBA)...")
            # Simulate a raw pixel framebuffer allocation in low memory
            framebuffer_size = 320 * 200 * 4
            print(f"Framebuffer initialized: {framebuffer_size} bytes allocated at 0xA000:0000.")
            print("Status: Ready for low-level pixel manipulation and rendering pipeline calls.")
"""

if 'elif cmd.upper() == "GO":' in code:
    code = code.replace('elif cmd.upper() == "GO":', paint_command + '\n        elif cmd.upper() == "GO":')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added OENEYEPAINT command to MOSFETQ-DOS v18.0!")
else:
    print("Could not locate command hook.")
