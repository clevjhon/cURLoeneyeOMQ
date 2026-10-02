with open("emu.py", "r") as f:
    code = f.read()

plot_command = """
        elif cmd.upper().startswith("PAINTPLOT"):
            parts = cmd.split()
            if len(parts) == 4:
                try:
                    x, y, color = int(parts[1]), int(parts[2]), int(parts[3])
                    if 0 <= x < 320 and 0 <= y < 200:
                        offset = (y * 320 + x) * 4
                        print(f"Plotting pixel at ({x}, {y}) with color 0x{color:08X} at framebuffer offset 0x{offset:05X}.")
                    else:
                        print("Error: Coordinates out of bounds (320x200).")
                except ValueError:
                    print("Usage: PAINTPLOT <x> <y> <color_hex>")
            else:
                print("Usage: PAINTPLOT <x> <y> <color_hex>")
"""

if 'elif cmd.upper() == "OENEYEPAINT":' in code:
    code = code.replace('elif cmd.upper() == "OENEYEPAINT":', plot_command + '\n        elif cmd.upper() == "OENEYEPAINT":')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added PAINTPLOT command to oeneyePaint!")
else:
    print("Could not locate OENEYEPAINT hook.")
