"""
OMQpython - Interactive Font Painter 2
Allows selecting a character and editing its pixel rows in OMQ.FNT.
"""

import os
import sys

FONT_FILE = "OMQ.FNT"
BYTES_PER_GLYPH = 16

def edit_glyph():
    if not os.path.exists(FONT_FILE):
        print(f"[-] Error: {FONT_FILE} not found!")
        return
    
    target_char = input("Enter a character to inspect/edit (e.g. A, H, O): ").upper()
    if not target_char:
        target_char = "A"
    
    char_code = ord(target_char[0])
    offset = (char_code * BYTES_PER_GLYPH) + 16  # Account for header
    
    with open(FONT_FILE, "r+b") as f:
        f.seek(offset)
        glyph_bytes = bytearray(f.read(BYTES_PER_GLYPH))
        
        print(f"\n--- Editing Glyph: '{target_char[0]}' (ASCII {char_code}) ---")
        for i, b in enumerate(glyph_bytes):
            binary_row = format(b, '08b')
            visual = binary_row.replace('0', '.').replace('1', '█')
            print(f"Row {i:2d}: {visual}  (byte: {b})")
            
        print("-" * 40)
        choice = input("Do you want to change a row byte? (y/n): ").lower()
        if choice == 'y':
            try:
                row_num = int(input("Enter row number (0-15): "))
                new_val = int(input("Enter new byte value (0-255): "))
                if 0 <= row_num < 16 and 0 <= new_val <= 255:
                    glyph_bytes[row_num] = new_val
                    f.seek(offset)
                    f.write(glyph_bytes)
                    print(f"[+] Row {row_num} updated successfully!")
                else:
                    print("[-] Invalid row or byte range.")
            except ValueError:
                print("[-] Please enter valid numbers.")

def main():
    print("[*] OMQpython Interactive Font Painter 2 Initialized.\n")
    edit_glyph()
    print("\n[+] Painter session closed.")

if __name__ == "__main__":
    main()

