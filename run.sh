#!/data/data/com.termux/files/usr/bin/bash
set -e
echo "[*] Building..."
make clean
make
echo "[*] File:"
file kernel.elf
echo "[*] Running in QEMU (Ctrl-a x to exit)..."
qemu-system-i386 -kernel kernel.elf -nographic
