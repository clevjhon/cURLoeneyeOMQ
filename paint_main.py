"""
OMQpython - Font Painter / Glyph Editor
A side program to inspect and modify pixel rows in OMQ.FNT.
"""

import os

FONT_FILE = "OMQ.FNT"
BYTES_PER_GLYPH = 16

def view_glyph(char):
    """Prints a zoom-in view of a specific character's byte data."""
    if not os.path.exists(FONT_FILE):
        print(f"[-] Error: {FONT_FILE} not found!")
        return
    
    char_code = ord(char)
    offset = (char_code * BYTES_PER_GLYPH) + 16 # Account for 16-byte header
    
    with open(FONT_FILE, "r+b") as f:
        f.seek(offset)
        glyph_bytes = f.read(BYTES_PER_GLYPH)
        
        print(f"\n--- [PAINT TOOL] Editing Glyph: '{char}' (ASCII {char_code}) ---")
        for i, b in enumerate(glyph_bytes):
            binary_row = format(b, '08b')
            visual = binary_row.replace('0', '.').replace('1', '█')
            print(f"Row {i:2d}: {visual}  (byte: {b})")

def main():
    print("[*] OMQpython Font Painter Initialized.")
    # Example: Inspect the letter 'H'
    view_glyph('H')
    print("\n[+] Use this side program to design and tweak your OMQ.FNT glyphs!")

if __name__ == "__main__":
    main()

