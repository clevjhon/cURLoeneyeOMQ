import struct, sys
DISK_SIZE = 1474560  # 1.44MB floppy
MSG = b"oeneye OS booted OK\r\n"
code = bytearray()
code += bytes([0xFA, 0x31,0xC0, 0x8E,0xD8, 0x8E,0xC0, 0x8E,0xD0, 0xBC,0x00,0x7C, 0xFB])  # cli; zero segs; sp=7C00; sti
code += bytes([0xBE, 0, 0])                                                                # mov si,msg (patched)
loop = len(code)
code += bytes([0xAC, 0x08,0xC0, 0x74,0x09, 0xB4,0x0E, 0xBB,0x07,0x00, 0xCD,0x10, 0xEB,0xF2])
code += bytes([0xFA, 0xF4, 0xEB,0xFD])                                                     # cli; hlt; jmp hlt
msg_off = len(code)
code[14:16] = struct.pack("<H", 0x7C00 + msg_off)
code += MSG + b"\x00"
assert len(code) <= 510
open("kernel.bin","wb").write(code)
img = bytearray(DISK_SIZE)
img[0:len(code)] = code
img[510:512] = b"\x55\xAA"
open("oeneye_os.img","wb").write(img)
print("kernel.bin", len(code), "bytes; oeneye_os.img", len(img), "bytes")
