MOSFETQ DOS  Gold 1.0.0.0.1
===========================
A small DOS-style operating system for 16-bit x86 PCs, written in assembly. Boots from a floppy image:

  mosfetq-dos-gold-1.0.0.0.1-3.5in-1.44M.img     3.5"  1.44 MB  (18 sectors/track)
  mosfetq-dos-gold-1.0.0.0.1-5.25in-1.2M.ximg    5.25" 1.2 MB   (15 sectors/track)
  Same OS, same files, same on-disk format (raw sectors). ".ximg" is only a name: rename it to .img if a tool
  insists. mosfetq-dos.xml describes both as one MIME type (application/x-mosfetq-dos-image, recognised by the
  boot-sector signature); "sh install-mime.sh" registers it.
  Try it:   qemu-system-i386 -fda mosfetq-dos-gold-1.0.0.0.1-3.5in-1.44M.img
            qemu-system-i386 -fda mosfetq-dos-gold-1.0.0.0.1-5.25in-1.2M.ximg
  (Everything below was tested in emu.py, a Python 8086 with a stub BIOS written for this project. It has NOT been
   run on QEMU or real hardware yet.)

What is in it
-------------
Shell            DIR TYPE DEL PRINT RUN ECHO MEM TIME DATE VER CLS REBOOT HELP; bare program names; 126-character lines
Files            FAT12 read + write (create, overwrite, delete, sequential write, auto-close on exit), .BAT and AUTOEXEC.BAT
Programs         .COM, .EXE (MZ, relocations), .BAT;  INT 21h: console, file create/open/read/write/seek/close/delete,
                 vectors, exit;  INT 20h;  INT 48h telemetry block (below)
Printing/plots   PRINT file -> LPT1 (raw: text or HPGL); INT 21h AH=05 and handle 4 (PRN)
OENEYE.EXE       8086 emulator + MINIX-style multitasker: up to 7 tasks, each on its own virtual 8086 with a private
                 64 KB window, pre-empted every 100 instructions; send/receive messages (INT 60h); reads OENEYE.RC when
                 started without arguments. Verified by ~170 random-program differential runs and 10 planted-bug
                 mutation checks. Tasks can use INT 48h too.
PAINT.COM        oeneyePaint: 64x64 pixel editor / skin designer, 16 colours, keyboard driven (arrows, SPACE, P pen,
                 0-9 A-F colours, [ ] cycle, X clear, S save, L load, Q quit). Saves standard 8-bit BMP (image/bmp).
TRAFO.COM        transformer circuit simulator (x87): saturating core, core loss, leakage, winding resistance, load,
                 clamped implicit time step. Integers on the command line, result line, C = TRAFO.CSV, H = HPGL to
                 PRN, results published over INT 48h. trafo/trafo.py is the reference engine and design helper:
                   python3 trafo/trafo.py sim VIN=300 RLOAD=2000       python3 trafo/trafo.py design --vp 230 --vs 24 --va 100 --ae 800
INT 48h          AH=00 version (AX=0102h, BX=32)  01 publish DS:DX (word 0 = 5254h)  02 poll into DS:DX  03 clear
Tools (host)     imgtool.py (list/add files in an image), fatcheck.py (independent FAT12 reader), fuzz/difftest for OENEYE

Not in this release (asked for, not built)
------------------------------------------
Virtual BIOS ROM at F000:0, guest interrupt vectors and port I/O for OENEYE; long file names (VFAT) and umlauts; NeXT-style
boot loader / SDK; Wi-Fi, LAN, multi-display, mouse, oeneyeFTP, user accounts / licensing servers, oeneyeSandbox, oeneyeVM,
oeneyeViewer, oeneyeOffice, STEP exchange; NASTRAN (.BDF) support. See the release notes in the chat for a proposed order.

Build and test (GNU as/ld + Python 3)
-------------------------------------
  ./build.sh                                   builds both images (mosfetq-dos.img, mosfetq-dos-1200.ximg)
  python3 test_dos.py                          161 checks, 3.5" image      (IMG=mosfetq-dos-1200.ximg: the 5.25" image)
  python3 run_part.py N                        one section of test_dos.py (1-9)
  python3 test_gold.py                         57 checks: both formats, paint, INT 48h
  python3 trafo/test_trafo.py                  14 physics checks of the reference engine
  python3 test_trafo_dos.py                    18 checks: TRAFO.COM equals the reference on 12 scenarios; CSV; HPGL
  python3 oeneye/difftest.py FIRST COUNT       differential fuzzing of OENEYE
