# MOSFETQ DOS 0.1 - a tiny bootable DOS-style OS (16-bit real mode, x86)
# Stage 1: 512-byte boot sector (0xAA55) loads Stage 2 with INT 13h.
# Stage 2: kernel + command shell (BIOS services only, no libc).
# Build: ./build.sh   Run: qemu-system-i386 -fda mosfetq-dos.img
.intel_syntax noprefix
.code16
.global _start
.text
# ---------------------------------------------------------------- STAGE 1
_start:
    .byte 0xEA          # far jmp 0000:boot (normalise CS:IP)
    .word boot
    .word 0
boot:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti
    cld
    mov [bootdrv], dl
    mov si, offset msg_load
    call puts
    mov cx, 3           # 3 retries
retry:
    push cx
    xor ah, ah          # reset disk
    mov dl, [bootdrv]
    int 0x13
    mov ax, 0x0210       # AH=02 read, AL=16 sectors
    mov bx, 0x7E00       # ES:BX destination
    mov cx, 0x0002       # cylinder 0, sector 2
    xor dh, dh           # head 0
    mov dl, [bootdrv]
    int 0x13
    pop cx               # POP keeps CF from INT 13h
    jnc kernel
    loop retry
    mov si, offset msg_err
    call puts
hang:
    hlt
    jmp hang
# ---- shared helpers (used by both stages) ----
putc:                    # AL = char
    push ax
    push bx
    mov ah, 0x0E
    mov bx, 0x0007
    int 0x10
    pop bx
    pop ax
    ret
puts:                    # SI = asciz string
    lodsb
    test al, al
    jz puts_done
    call putc
    jmp puts
puts_done:
    ret
bootdrv: .byte 0
msg_load: .asciz "Loading MOSFETQ DOS...\r\n"
msg_err: .asciz "Disk error. System halted."
.org 510
.word 0xAA55
# ---------------------------------------------------------------- STAGE 2
kernel:
    call cls
    mov si, offset m_banner
    call puts
main:
    mov si, offset m_prompt
    call puts
    call readline
    call dispatch
    jmp main
cls:
    mov ax, 0x0003       # set 80x25 text mode = clear screen
    int 0x10
    ret
crlf:
    mov si, offset m_crlf
    call puts
    ret
# ---- line input with backspace, result in buf (asciz) ----
readline:
    mov di, offset buf
    xor cx, cx
rl_key:
    xor ah, ah
    int 0x16             # wait for key
    cmp al, 13
    je rl_done
    cmp al, 8
    je rl_bs
    cmp al, 32
    jb rl_key
    cmp cx, 63
    jae rl_key
    stosb
    inc cx
    call putc
    jmp rl_key
rl_bs:
    test cx, cx
    jz rl_key
    dec di
    dec cx
    mov al, 8
    call putc
    mov al, 32
    call putc
    mov al, 8
    call putc
    jmp rl_key
rl_done:
    xor al, al
    stosb
    call crlf
    ret
# ---- match: SI=input, DI=UPPERCASE name. ZF=1 on match (SI -> after name)
match:
    push si
m_loop:
    mov al, [si]
    cmp al, 'a'
    jb m_cmp
    cmp al, 'z'
    ja m_cmp
    sub al, 32
m_cmp:
    mov ah, [di]
    test ah, ah
    jz m_end
    cmp al, ah
    jne m_no
    inc si
    inc di
    jmp m_loop
m_end:
    test al, al
    jz m_yes
    cmp al, ' '
    je m_yes
m_no:
    pop si
    or al, 1             # ZF=0
    ret
m_yes:
    pop ax
    cmp al, al           # ZF=1
    ret
skipsp:
    cmp byte ptr [si], ' '
    jne skipsp_ret
    inc si
    jmp skipsp
skipsp_ret:
    ret
strlen:                  # SI -> AX = length
    push si
    xor ax, ax
sl_loop:
    cmp byte ptr [si], 0
    je sl_done
    inc si
    inc ax
    jmp sl_loop
sl_done:
    pop si
    ret
print_dec:                # AX = unsigned number
    push ax
    push bx
    push cx
    push dx
    xor cx, cx
    mov bx, 10
pd_div:
    xor dx, dx
    div bx
    push dx
    inc cx
    test ax, ax
    jnz pd_div
pd_out:
    pop ax
    add al, '0'
    call putc
    loop pd_out
    pop dx
    pop cx
    pop bx
    pop ax
    ret
put_bcd:                  # AL = packed BCD
    push ax
    shr al, 4
    add al, '0'
    call putc
    pop ax
    and al, 0x0F
    add al, '0'
    call putc
    ret
# ---- command dispatcher ----
dispatch:
    mov si, offset buf
    cmp byte ptr [si], 0
    je disp_ret
    mov di, offset c_help
    call match
    jz do_help
    mov di, offset c_ver
    call match
    jz do_ver
    mov di, offset c_cls
    call match
    jz cls
    mov di, offset c_echo
    call match
    jz do_echo
    mov di, offset c_mem
    call match
    jz do_mem
    mov di, offset c_time
    call match
    jz do_time
    mov di, offset c_date
    call match
    jz do_date
    mov di, offset c_dir
    call match
    jz do_dir
    mov di, offset c_type
    call match
    jz do_type
    mov di, offset c_reboot
    call match
    jz do_reboot
    mov si, offset m_bad
    call puts
disp_ret:
    ret
do_help:
    mov si, offset m_help
    call puts
    ret
do_ver:
    mov si, offset m_ver
    call puts
    ret
do_echo:
    call skipsp
    call puts
    jmp crlf
do_mem:
    int 0x12              # AX = conventional memory in KB
    call print_dec
    mov si, offset m_mem
    call puts
    ret
do_time:
    mov ah, 2
    int 0x1A               # CH=hh CL=mm DH=ss (BCD)
    mov al, ch
    call put_bcd
    mov al, ':'
    call putc
    mov al, cl
    call put_bcd
    mov al, ':'
    call putc
    mov al, dh
    call put_bcd
    jmp crlf
do_date:
    mov ah, 4
    int 0x1A                # CH=cc CL=yy DH=mm DL=dd (BCD)
    mov al, ch
    call put_bcd
    mov al, cl
    call put_bcd
    mov al, '-'
    call putc
    mov al, dh
    call put_bcd
    mov al, '-'
    call putc
    mov al, dl
    call put_bcd
    jmp crlf
do_dir:
    mov si, offset m_dirhdr
    call puts
    mov bx, offset files
    xor dx, dx
dir_loop:
    mov si, [bx]
    test si, si
    jz dir_end
    push si
    call puts
    pop si
    call strlen
    mov cx, 14
    sub cx, ax
dir_pad:
    mov al, ' '
    call putc
    loop dir_pad
    mov si, [bx+2]
    call strlen
    call print_dec
    mov si, offset m_bytes
    call puts
    inc dx
    add bx, 4
    jmp dir_loop
dir_end:
    mov ax, dx
    call print_dec
    mov si, offset m_files
    call puts
    ret
do_type:
    call skipsp
    cmp byte ptr [si], 0
    je type_usage
    mov bx, offset files
type_loop:
    mov di, [bx]
    test di, di
    jz type_nf
    call match
    jz type_found
    add bx, 4
    jmp type_loop
type_found:
    mov si, [bx+2]
    call puts
    jmp crlf
type_nf:
    mov si, offset m_nofile
    call puts
    ret
type_usage:
    mov si, offset m_usage
    call puts
    ret
do_reboot:
    .byte 0xEA            # far jmp FFFF:0000 (BIOS reset vector)
    .word 0x0000
    .word 0xFFFF
# ---- data & embedded files ----
c_help: .asciz "HELP"
c_ver: .asciz "VER"
c_cls: .asciz "CLS"
c_echo: .asciz "ECHO"
c_mem: .asciz "MEM"
c_time: .asciz "TIME"
c_date: .asciz "DATE"
c_dir: .asciz "DIR"
c_type: .asciz "TYPE"
c_reboot: .asciz "REBOOT"
m_prompt: .asciz "A:\\"
m_crlf: .asciz "\r\n"
m_bad: .asciz "Bad command or file name\r\n"
m_usage: .asciz "Usage: TYPE filename\r\n"
m_nofile: .asciz "File not found\r\n"
m_mem: .asciz " KB conventional memory\r\n"
m_bytes: .asciz " bytes\r\n"
m_files: .asciz " file(s)\r\n"
m_dirhdr: .asciz " Volume in drive A is MOSFETQ\r\n\r\n"
m_ver: .asciz "MOSFETQ DOS 0.1 (real mode, BIOS services)\r\n"
m_banner: .ascii "MOSFETQ DOS 0.1\r\n"
    .asciz "Type HELP for a list of commands.\r\n\r\n"
m_help: .ascii "HELP this list\r\n"
    .ascii "VER show version\r\n"
    .ascii "CLS clear the screen\r\n"
    .ascii "ECHO x print text\r\n"
    .ascii "MEM conventional memory size\r\n"
    .ascii "TIME RTC time DATE RTC date\r\n"
    .ascii "DIR list files TYPE f show a file\r\n"
    .asciz "REBOOT restart the machine\r\n"
files:
    .word f1n, f1d
    .word f2n, f2d
    .word 0
f1n: .asciz "README.TXT"
f1d: .asciz "MOSFETQ DOS is a tiny DOS-style OS: boot sector, kernel and shell.\r\nAll files here are built into the kernel image (no disk filesystem yet)."
f2n: .asciz "TODO.TXT"
f2d: .asciz "1. FAT12 driver (INT 13h) 2. RUN for .COM files 3. INT 21h services"
buf: .space 64
kernel_end:
