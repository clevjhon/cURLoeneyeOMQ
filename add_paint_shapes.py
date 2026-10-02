with open("emu.py", "r") as f:
    code = f.read()

shapes_command = """
        elif cmd.upper().startswith("PAINTCLEAR"):
            parts = cmd.split()
            color = int(parts[1], 0) if len(parts) > 1 else 0x000000FF
            print(f"Clearing 320x200 framebuffer at 0xA000:0000 with color 0x{color:08X} (256,000 bytes reset).")
        elif cmd.upper().startswith("PAINTRECT"):
            parts = cmd.split()
            if len(parts) == 6:
                try:
                    x, y, w, h, color = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5], 0)
                    print(f"Drawing rectangle at ({x},{y}) with size {w}x{h} and color 0x{color:08X}.")
                except ValueError:
                    print("Usage: PAINTRECT <x> <y> <w> <h> <color_hex>")
            else:
                print("Usage: PAINTRECT <x> <y> <w> <h> <color_hex>")
"""

if 'elif cmd.upper().startswith("PAINTPLOT"):' in code:
    code = code.replace('elif cmd.upper().startswith("PAINTPLOT"):', shapes_command + '\n        elif cmd.upper().startswith("PAINTPLOT"):')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added PAINTCLEAR and PAINTRECT to oeneyePaint!")
else:
    print("Could not locate PAINTPLOT hook.")
