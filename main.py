#!/usr/bin/env python3
"""
cURLoeneyeOMQ - Unified Binary Font Engine, Glyph Painter, and Banner Renderer
Project repository: https://github.com/clevjhon/cURLoeneyeOMQ
"""

import os
import sys

# Constants
FONT_FILE = "OMQ.FNT"
GLYPH_WIDTH = 8
GLYPH_HEIGHT = 8
BYTES_PER_GLYPH = 8

ANSI_RESET = "\033[0m"
ANSI_BG_BLACK = "\033[40m"
ANSI_BG_WHITE = "\033[47m"
ANSI_FG_GREEN = "\033[32m"
ANSI_FG_CYAN = "\033[36m"

def create_default_font():
    print(f"[*] Initializing default font database -> {FONT_FILE}")
    blank_glyph = b"\x00\x00\x00\x00\x00\x00\x00\x00"
    with open(FONT_FILE, "wb") as f:
        for i in range(256):
            if 33 <= i <= 126:
                pattern = bytes([0x18, 0x3C, 0x3C, 0x18, 0x18, 0x18, 0x18, 0x3C])
                f.write(pattern)
            else:
                f.write(blank_glyph)

def load_glyph(char_code):
    if not os.path.exists(FONT_FILE):
        create_default_font()
    with open(FONT_FILE, "rb") as f:
        f.seek(char_code * BYTES_PER_GLYPH)
        data = f.read(BYTES_PER_GLYPH)
        if len(data) < BYTES_PER_GLYPH:
            data = data + b"\x00" * (BYTES_PER_GLYPH - len(data))
        return bytearray(data)

def save_glyph(char_code, glyph_data):
    if not os.path.exists(FONT_FILE):
        create_default_font()
    with open(FONT_FILE, "r+b") as f:
        f.seek(char_code * BYTES_PER_GLYPH)
        f.write(bytes(glyph_data))

def render_banner(text):
    print(f"\n{ANSI_FG_CYAN}[*] Rendering Banner: '{text}'{ANSI_RESET}")
    glyph_rows = [load_glyph(ord(c)) for c in text]
    for row_idx in range(GLYPH_HEIGHT):
        line_str = ""
        for g in glyph_rows:
            row_byte = g[row_idx]
            for bit_idx in range(GLYPH_WIDTH - 1, -1, -1):
                bit = (row_byte >> bit_idx) & 1
                if bit:
                    line_str += f"{ANSI_BG_WHITE}  {ANSI_RESET}"
                else:
                    line_str += f"{ANSI_BG_BLACK}  {ANSI_RESET}"
            line_str += " "
        print(line_str)
    print()

if __name__ == "__main__":
    if not os.path.exists(FONT_FILE):
        create_default_font()
    if len(sys.argv) > 1 and sys.argv[1] == "banner":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "OMQ ENGINE"
        render_banner(msg)
    else:
        render_banner("OMQ FONT")
