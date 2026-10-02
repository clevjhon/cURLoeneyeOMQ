#!/bin/sh
# Needs GNU binutils (as, ld) and Python 3. Produces mosfetq-dos.img (1.44 MB FAT12 floppy).
set -e
as --32 -o mosfetq-dos.o mosfetq-dos.s
ld -m elf_i386 -Ttext=0x7C00 --oformat binary -o mosfetq-dos.bin mosfetq-dos.o
python3 mkimage.py
