# 16-bit x86 Real Mode Machine Code:
# - Sets up a text string printing routine using BIOS int 0x10 (teletype mode)
# - Prints "oeneye-00x00 active: system operational."
# - Enters an infinite halt loop
# - Pads out to 510 bytes and adds the 0xAA55 boot signature

boot_code = bytearray([
    0xbc, 0x00, 0x7c,              # mov sp, 0x7c00
    0xbe, 0x1c, 0x7c,              # mov si, msg (offset of message)
    # .loop:
    0xac,                          # lodsb
    0x3c, 0x00,                    # cmp al, 0
    0x74, 0x0b,                    # je .done
    0xb4, 0x0e,                    # mov ah, 0x0e
    0xcd, 0x10,                    # int 0x10
    0xeb, 0xf4,                    # jmp .loop
    # .done:
    0xf4,                          # hlt
    0xeb, 0xfd,                    # jmp $ (infinite loop)
    # Message string:
]) + b"oeneye-00x00 active: system operational.\r\n\0"

# Pad the rest of the 512-byte boot sector with zeros
boot_code += b'\x00' * (510 - len(boot_code))

# Add standard boot signature (0x55AA)
boot_code += b'\x55\xaa'

# Create the full 1.44MB floppy disk image (1,474,560 bytes)
full_image = boot_code + (b'\x00' * (1474560 - len(boot_code)))

with open("oeneye-00x00.img", "wb") as f:
    f.write(full_image)

print("Successfully generated bootable 1.44MB floppy image: oeneye-00x00.img")
