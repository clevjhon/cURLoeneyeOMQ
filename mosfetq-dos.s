# MOSFETQ DOS 0.3 - tiny bootable DOS-style OS (16-bit real mode, x86)
# Stage 1: boot sector with FAT12 BPB, loads the kernel with INT 13h.
# Stage 2: kernel + shell + read-only FAT12 driver (DIR, TYPE) +
#          .COM program loader (RUN / bare name) with a minimal INT 21h.
#
# Disk layout (1.44 MB floppy):
#   LBA 0        boot sector (BPB)
#   LBA 1-16     kernel (16 reserved sectors, BPB says reserved = 17)
#   LBA 17-25    FAT #1      LBA 26-34  FAT #2
#   LBA 35-48    root dir (224 entries)     LBA 49+ data (cluster 2 = LBA 49)

.intel_syntax noprefix
.code16
.global _start
.text

.equ SPT,       18
.equ ROOT_LBA,  35
.equ ROOT_SECT, 14
.equ ROOT_ENT,  224
.equ FAT_LBA,   17
.equ FAT_SECT,  9
.equ DATA_LBA,  49
.equ ROOTBUF,   0xA000          # 7168 bytes
.equ FATBUF,    0xC000          # 4608 bytes
.equ FILEBUF,   0xD400          # 512 bytes
.equ COMSEG,    0x1000          # .COM programs live at 1000:0100
.equ MAXCOM,    0xF000          # largest .COM we accept (bytes)

# ---------------------------------------------------------------- STAGE 1
_start:
    .byte 0xEB, 0x3C, 0x90          # jmp short boot ; nop
    .ascii "MOSFETQ "               # 0x03 OEM name
    .word 512                       # 0x0B bytes per sector
    .byte 1                         # 0x0D sectors per cluster
    .word 17                        # 0x0E reserved sectors (boot + kernel)
    .byte 2                         # 0x10 number of FATs
    .word 224                       # 0x11 root entries
    .word 2880                      # 0x13 total sectors
    .byte 0xF0                      # 0x15 media descriptor
    .word 9                         # 0x16 sectors per FAT
    .word 18                        # 0x18 sectors per track
    .word 2                         # 0x1A heads
    .long 0                         # 0x1C hidden sectors
    .long 0                         # 0x20 total sectors (32-bit)
    .byte 0                         # 0x24 drive number
    .byte 0                         # 0x25 reserved
    .byte 0x29                      # 0x26 extended boot signature
    .long 0x4D4F5346                # 0x27 volume serial
    .ascii "MOSFETQ    "            # 0x2B volume label
    .ascii "FAT12   "               # 0x36 file system type
.org 0x3E
boot:
    .byte 0xEA                      # far jmp 0000:boot2 (normalise CS:IP)
    .word boot2
    .word 0
boot2:
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
    mov cx, 3                       # 3 retries
retry:
    push cx
    xor ah, ah                      # reset disk
    mov dl, [bootdrv]
    int 0x13
    mov ax, 0x0210                  # AH=02 read, AL=16 sectors
    mov bx, 0x7E00                  # ES:BX destination
    mov cx, 0x0002                  # cylinder 0, sector 2 (= LBA 1)
    xor dh, dh                      # head 0
    mov dl, [bootdrv]
    int 0x13
    pop cx                          # POP keeps CF from INT 13h
    jnc kernel
    loop retry
    mov si, offset msg_err
    call puts
hang:
    hlt
    jmp hang

# ---- shared helpers (used by both stages) ----
putc:                               # AL = char
    push ax
    push bx
    mov ah, 0x0E
    mov bx, 0x0007
    int 0x10
    pop bx
    pop ax
    ret

puts:                               # SI = asciz string
    lodsb
    test al, al
    jz puts_done
    call putc
    jmp puts
puts_done:
    ret

bootdrv:  .byte 0
msg_load: .asciz "Loading MOSFETQ DOS...\r\n"
msg_err:  .asciz "Disk error. System halted."

.org 510
.word 0xAA55

# ---------------------------------------------------------------- STAGE 2
kernel:
    call cls
    mov si, offset m_banner
    call puts
    call init_fs
    call install_ints
main:
    mov si, offset m_prompt
    call puts
    call readline
    call dispatch
    jmp main

cls:
    mov ax, 0x0003                  # set 80x25 text mode = clear screen
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
    int 0x16                        # wait for key
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
    call upcase
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
    or al, 1                        # ZF=0
    ret
m_yes:
    pop ax
    cmp al, al                      # ZF=1
    ret

upcase:                             # AL -> uppercase
    cmp al, 'a'
    jb up_ret
    cmp al, 'z'
    ja up_ret
    sub al, 32
up_ret:
    ret

skipsp:
    cmp byte ptr [si], ' '
    jne skipsp_ret
    inc si
    jmp skipsp
skipsp_ret:
    ret

strlen:                             # SI -> AX = length
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

print_dec:                          # AX = unsigned 16-bit number
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

print_dec32:                        # DX:AX = unsigned 32-bit number
    push ax
    push bx
    push cx
    push dx
    push si
    mov bx, 10
    xor cx, cx
p32_loop:
    mov si, ax                      # save low word
    mov ax, dx                      # high word
    xor dx, dx
    div bx                          # AX = hi/10, DX = hi%10
    xchg ax, si                     # AX = low word, SI = hi/10
    div bx                          # DX:AX / 10 -> AX = q_lo, DX = digit
    push dx
    inc cx
    mov dx, si                      # DX:AX = quotient
    mov si, ax
    or si, dx
    jnz p32_loop
p32_out:
    pop ax
    add al, '0'
    call putc
    loop p32_out
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

put_bcd:                            # AL = packed BCD
    push ax
    shr al, 4
    add al, '0'
    call putc
    pop ax
    and al, 0x0F
    add al, '0'
    call putc
    ret

# ================================================================ FAT12
# read_sector: AX = LBA, ES:BX = destination. CF=1 on error.
# Preserves every register.
read_sector:
    push ax
    push bx
    push cx
    push dx
    push si
    xor dx, dx
    mov cx, SPT
    div cx                          # AX = track, DX = sector-1
    inc dl
    mov cl, dl                      # CL = sector (1-based)
    mov dh, al
    and dh, 1                       # DH = head
    shr ax, 1
    mov ch, al                      # CH = cylinder
    mov [chs_cx], cx
    mov dl, [bootdrv]
    mov [chs_dx], dx
    mov si, 3
rs_try:
    mov cx, [chs_cx]
    mov dx, [chs_dx]
    mov ax, 0x0201                  # read 1 sector
    int 0x13
    jnc rs_ok
    xor ah, ah                      # reset disk, then retry
    mov dl, [bootdrv]
    int 0x13
    dec si
    jnz rs_try
    stc
    jmp rs_out
rs_ok:
    clc
rs_out:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

# read_sectors: AX = first LBA, BX = destination, CX = count. CF=1 on error.
read_sectors:
    push ax
    push bx
    push cx
rss_loop:
    call read_sector
    jc rss_out
    inc ax
    add bx, 512
    loop rss_loop
    clc
rss_out:
    pop cx
    pop bx
    pop ax
    ret

# init_fs: cache the root directory and the FAT in RAM.
init_fs:
    mov byte ptr [fs_ok], 0
    mov ax, ROOT_LBA
    mov bx, ROOTBUF
    mov cx, ROOT_SECT
    call read_sectors
    jc ifs_err
    mov ax, FAT_LBA
    mov bx, FATBUF
    mov cx, FAT_SECT
    call read_sectors
    jc ifs_err
    mov byte ptr [fs_ok], 1
    ret
ifs_err:
    mov si, offset m_fserr
    call puts
    ret

# fat_next: AX = cluster -> AX = next cluster (FAT12 entry).
fat_next:
    push bx
    push cx
    mov cx, ax
    mov bx, ax
    shr bx, 1
    add bx, ax                      # BX = n + n/2
    add bx, FATBUF
    mov ax, [bx]
    test cl, 1
    jz fx_even
    shr ax, 4
    jmp fx_end
fx_even:
    and ax, 0x0FFF
fx_end:
    pop cx
    pop bx
    ret

# fmt_name: BX = dir entry -> "NAME.EXT" asciz in namebuf
fmt_name:
    push si
    push di
    push cx
    mov si, bx
    mov di, offset namebuf
    mov cx, 8
fn_n:
    lodsb
    cmp al, ' '
    je fn_nend
    stosb
    loop fn_n
fn_nend:
    cmp byte ptr [bx+8], ' '
    je fn_done
    mov al, '.'
    stosb
    lea si, [bx+8]
    mov cx, 3
fn_e:
    lodsb
    cmp al, ' '
    je fn_done
    stosb
    loop fn_e
fn_done:
    xor al, al
    stosb
    pop cx
    pop di
    pop si
    ret

# make_fcb: SI = "name.ext" -> 11-byte space padded uppercase in fcbname
make_fcb:
    push ax
    push cx
    push si
    push di
    mov di, offset fcbname
    mov cx, 11
mf_fill:
    mov byte ptr [di], ' '
    inc di
    loop mf_fill
    mov di, offset fcbname
    mov cx, 8
mf_n:
    mov al, [si]
    test al, al
    jz mf_done
    cmp al, ' '
    je mf_done
    cmp al, '.'
    je mf_dot
    call upcase
    mov [di], al
    inc di
    inc si
    loop mf_n
    cmp byte ptr [si], '.'
    jne mf_done
mf_dot:
    inc si                          # skip the '.'
    mov di, offset fcbname + 8
    mov cx, 3
mf_e:
    mov al, [si]
    test al, al
    jz mf_done
    cmp al, ' '
    je mf_done
    call upcase
    mov [di], al
    inc di
    inc si
    loop mf_e
mf_done:
    pop di
    pop si
    pop cx
    pop ax
    ret

# find_file: search root for fcbname. CF=0 and BX = entry if found.
find_file:
    push cx
    push dx
    push si
    push di
    mov bx, ROOTBUF
    mov cx, ROOT_ENT
ff_next:
    cmp byte ptr [bx], 0
    je ff_no
    mov si, bx
    mov di, offset fcbname
    mov dx, 11
ff_cmp:
    lodsb
    cmp al, [di]
    jne ff_ne
    inc di
    dec dx
    jnz ff_cmp
    clc
    jmp ff_out
ff_ne:
    add bx, 32
    loop ff_next
ff_no:
    stc
ff_out:
    pop di
    pop si
    pop dx
    pop cx
    ret

# print_bytes: SI = buffer, CX = count (LF -> CRLF, CR dropped, ^Z ends)
print_bytes:
    push ax
    push cx
    push si
pb_loop:
    test cx, cx
    jz pb_done
    lodsb
    dec cx
    cmp al, 0x0D
    je pb_loop
    cmp al, 0x1A
    je pb_done
    cmp al, 0x0A
    jne pb_ch
    mov al, 13
    call putc
    mov al, 10
pb_ch:
    call putc
    jmp pb_loop
pb_done:
    pop si
    pop cx
    pop ax
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
    mov di, offset c_run
    call match
    jz do_run
    mov si, offset buf              # not built in: try NAME.COM on the disk
    call run_com
    jnc disp_ret
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
    int 0x12                        # AX = conventional memory in KB
    call print_dec
    mov si, offset m_mem
    call puts
    ret

do_time:
    mov ah, 2
    int 0x1A                        # CH=hh CL=mm DH=ss (BCD)
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
    int 0x1A                        # CH=cc CL=yy DH=mm DL=dd (BCD)
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
    cmp byte ptr [fs_ok], 0
    je no_fs
    mov si, offset m_dirhdr
    call puts
    mov word ptr [dcount], 0
    mov word ptr [dircount], 0
    mov bx, ROOTBUF
    mov cx, ROOT_ENT
dir_next:
    mov al, [bx]
    test al, al
    jz dir_end                      # 0x00 = no more entries
    cmp al, 0xE5
    je dir_skip                     # deleted
    test byte ptr [bx+11], 0x08
    jnz dir_skip                    # volume label / long-name entry
    call print_entry
    test byte ptr [bx+11], 0x10
    jnz dir_isdir
    inc word ptr [dcount]
    jmp dir_skip
dir_isdir:
    inc word ptr [dircount]
dir_skip:
    add bx, 32
    loop dir_next
dir_end:
    mov ax, [dcount]
    call print_dec
    mov si, offset m_files
    call puts
    mov ax, [dircount]
    call print_dec
    mov si, offset m_dirs
    call puts
    ret

no_fs:
    mov si, offset m_nofs
    call puts
    ret

# print_entry: BX = directory entry
print_entry:
    push ax
    push cx
    push dx
    push si
    call fmt_name
    mov si, offset namebuf
    call puts
    mov si, offset namebuf
    call strlen
    mov cx, 14
    sub cx, ax
pe_pad:
    mov al, ' '
    call putc
    loop pe_pad
    test byte ptr [bx+11], 0x10
    jz pe_size
    mov si, offset m_dirtag
    call puts
    jmp pe_done
pe_size:
    mov ax, [bx+28]
    mov dx, [bx+30]
    call print_dec32
    mov si, offset m_bytes
    call puts
pe_done:
    pop si
    pop dx
    pop cx
    pop ax
    ret

do_type:
    cmp byte ptr [fs_ok], 0
    je no_fs
    call skipsp
    cmp byte ptr [si], 0
    je type_usage
    call make_fcb
    call find_file
    jc type_nf
    test byte ptr [bx+11], 0x18
    jnz type_nf                     # directory or label
    mov cx, [bx+26]                 # first cluster
    mov ax, [bx+28]
    mov [rem_lo], ax
    mov ax, [bx+30]
    mov [rem_hi], ax
type_loop:
    cmp cx, 2
    jb type_done
    cmp cx, 0xFF8
    jae type_done
    mov ax, [rem_lo]
    or ax, [rem_hi]
    jz type_done                    # nothing left
    mov ax, cx
    add ax, DATA_LBA - 2            # cluster -> LBA (1 sector/cluster)
    mov bx, FILEBUF
    call read_sector
    jc type_err
    mov ax, 512                     # AX = bytes to show from this sector
    cmp word ptr [rem_hi], 0
    jne type_n
    cmp word ptr [rem_lo], 512
    jae type_n
    mov ax, [rem_lo]
type_n:
    sub [rem_lo], ax
    sbb word ptr [rem_hi], 0
    push cx
    mov cx, ax
    mov si, FILEBUF
    call print_bytes
    pop cx
    mov ax, cx
    call fat_next
    mov cx, ax
    jmp type_loop
type_done:
    jmp crlf
type_nf:
    mov si, offset m_nofile
    call puts
    ret
type_err:
    mov si, offset m_fserr
    call puts
    ret
type_usage:
    mov si, offset m_usage
    call puts
    ret

do_reboot:
    .byte 0xEA                      # far jmp FFFF:0000 (BIOS reset vector)
    .word 0x0000
    .word 0xFFFF

# ================================================================ .COM LOADER
# install_ints: hook INT 20h (terminate) and INT 21h (DOS services).
install_ints:
    mov word ptr [0x80], offset int20h
    mov word ptr [0x82], 0
    mov word ptr [0x84], offset int21h
    mov word ptr [0x86], 0
    ret

do_run:                             # RUN name [args]
    call skipsp
    cmp byte ptr [si], 0
    je run_usage
    call run_com
    jc run_nf
    ret
run_nf:
    mov si, offset m_nofile
    call puts
    ret
run_usage:
    mov si, offset m_runusage
    call puts
    ret

# run_com: SI = program name token (arguments follow it in buf).
# Returns CF=1 if there is no such .COM file; CF=0 if it ran (or an error
# message was already printed).
run_com:
    cmp byte ptr [fs_ok], 0
    je rc_nf
    mov [argname], si
    call make_fcb
    cmp byte ptr [fcbname+8], ' '
    jne rc_chkext
    mov byte ptr [fcbname+8], 'C'   # no extension typed: assume .COM
    mov byte ptr [fcbname+9], 'O'
    mov byte ptr [fcbname+10], 'M'
rc_chkext:
    cmp byte ptr [fcbname+8], 'C'
    jne rc_nf
    cmp byte ptr [fcbname+9], 'O'
    jne rc_nf
    cmp byte ptr [fcbname+10], 'M'
    jne rc_nf
    call find_file
    jc rc_nf
    test byte ptr [bx+11], 0x18
    jnz rc_nf                       # directory / label
    cmp word ptr [bx+30], 0
    jne rc_big
    mov ax, [bx+28]
    test ax, ax
    jz rc_bad                       # empty file
    cmp ax, MAXCOM
    ja rc_big
    mov cx, [bx+26]                 # first cluster
    mov ax, COMSEG
    mov es, ax
    mov bx, 0x0100                  # ES:BX = 1000:0100
rc_load:
    cmp cx, 2
    jb rc_loaded
    cmp cx, 0xFF8
    jae rc_loaded
    cmp bx, 0xF300
    ja rc_bad                       # chain longer than the size allows
    mov ax, cx
    add ax, DATA_LBA - 2
    call read_sector
    jc rc_rderr
    add bx, 512
    mov ax, cx
    call fat_next
    mov cx, ax
    jmp rc_load
rc_loaded:
    cld
    xor di, di                      # ES = COMSEG: build the PSP
    xor ax, ax
    mov cx, 128
    rep stosw                       # zero 1000:0000-00FF
    xor di, di
    mov ax, 0x20CD                  # PSP:0000 = INT 20h
    stosw
    mov ax, 0xA000                  # PSP:0002 = top of memory segment
    stosw
    mov si, [argname]
rc_tok:                             # skip the program name
    mov al, [si]
    test al, al
    jz rc_noargs
    cmp al, ' '
    je rc_gotsp
    inc si
    jmp rc_tok
rc_gotsp:
    call skipsp
    cmp byte ptr [si], 0
    je rc_noargs
    mov di, 0x81                    # command tail: " args" CR, length at 0x80
    mov al, ' '
    stosb
    mov cx, 1
rc_cp:
    lodsb
    test al, al
    jz rc_cpdone
    stosb
    inc cx
    cmp cx, 120
    jb rc_cp
rc_cpdone:
    mov al, 13
    stosb
    mov di, 0x80
    mov al, cl
    stosb
    jmp rc_launch
rc_noargs:
    mov di, 0x81
    mov al, 13
    stosb
rc_launch:
    xor ax, ax
    mov es, ax
    mov [ksp], sp                   # INT 20h / 21h-4Ch come back here
    mov ax, COMSEG
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0xFFFE
    xor ax, ax
    push ax                         # a plain RET jumps to PSP:0000 = INT 20h
    xor bx, bx
    mov cx, 0x00FF
    xor dx, dx
    xor si, si
    xor di, di
    xor bp, bp
    .byte 0xEA                      # jmp far 1000:0100
    .word 0x0100
    .word COMSEG
rc_nf:
    stc
    ret
rc_big:
    mov si, offset m_big
    jmp rc_errmsg
rc_bad:
    mov si, offset m_badprog
    jmp rc_errmsg
rc_rderr:
    mov si, offset m_fserr
rc_errmsg:
    xor ax, ax
    mov es, ax
    call puts
    clc
    ret

# run_done: the program ended (we are back on the kernel stack, DS=ES=SS=0)
run_done:
    cld
    mov al, [exitcode]
    test al, al
    jz rd_ret
    mov si, offset m_exitcode
    call puts                       # (clobbers AL, so reload the code)
    mov al, [exitcode]
    xor ah, ah
    call print_dec
    call crlf
rd_ret:
    clc
    ret

# ---- INT 20h / INT 21h (entered with the PROGRAM's DS/ES/SS) ----
int20h:
    xor al, al
    jmp s_exit

int21h:
    sti
    cmp ah, 0x01
    je s_getche
    cmp ah, 0x02
    je s_putch
    cmp ah, 0x07
    je s_getch
    cmp ah, 0x08
    je s_getch
    cmp ah, 0x09
    je s_print
    cmp ah, 0x0A
    je s_bufin
    cmp ah, 0x0B
    je s_kbhit
    cmp ah, 0x25
    je s_setvec
    cmp ah, 0x30
    je s_version
    cmp ah, 0x35
    je s_getvec
    cmp ah, 0x4C
    je s_exit
    push bp                         # unknown function: AX=1, CF=1
    mov bp, sp
    or word ptr [bp+6], 1           # CF in the saved FLAGS
    pop bp
    mov ax, 1
    iret

s_getche:                           # 01: read key with echo -> AL
    xor ah, ah
    int 0x16
    call putc
    iret

s_getch:                            # 07/08: read key, no echo -> AL
    xor ah, ah
    int 0x16
    iret

s_putch:                            # 02: print DL
    push ax
    mov al, dl
    call putc
    pop ax
    iret

s_print:                            # 09: print '$'-terminated string at DS:DX
    push ax
    push si
    mov si, dx
sp_loop:
    lodsb
    cmp al, '$'
    je sp_done
    call putc
    jmp sp_loop
sp_done:
    pop si
    pop ax
    iret

s_bufin:                            # 0A: buffered input at DS:DX [max][len][text..CR]
    push ax
    push bx
    push cx
    mov bx, dx
    xor cx, cx                      # CL = characters so far
bi_key:
    xor ah, ah
    int 0x16
    cmp al, 13
    je bi_done
    cmp al, 8
    je bi_bs
    cmp al, 32
    jb bi_key
    mov ah, [bx]                    # room for max-1 characters (CR needs a byte)
    dec ah
    cmp cl, ah
    jae bi_key
    push bx
    add bx, cx
    mov [bx+2], al
    pop bx
    inc cl
    call putc
    jmp bi_key
bi_bs:
    test cl, cl
    jz bi_key
    dec cl
    mov al, 8
    call putc
    mov al, 32
    call putc
    mov al, 8
    call putc
    jmp bi_key
bi_done:
    mov [bx+1], cl
    push bx
    add bx, cx
    mov byte ptr [bx+2], 13
    pop bx
    mov al, 13
    call putc
    mov al, 10
    call putc
    pop cx
    pop bx
    pop ax
    iret

s_kbhit:                            # 0B: AL = FF if a key is waiting, else 00
    mov ah, 1
    int 0x16
    mov al, 0
    jz kb_ret
    mov al, 0xFF
kb_ret:
    iret

s_setvec:                           # 25: AL = int number, DS:DX = handler
    push ax
    push bx
    push cx
    push ds
    mov cx, ds
    xor bx, bx
    mov ds, bx
    xor ah, ah
    shl ax, 2
    mov bx, ax
    mov [bx], dx
    mov [bx+2], cx
    pop ds
    pop cx
    pop bx
    pop ax
    iret

s_getvec:                           # 35: AL = int number -> ES:BX
    push ax
    push ds
    xor bx, bx
    mov ds, bx
    xor ah, ah
    shl ax, 2
    mov bx, ax
    mov ax, [bx+2]
    mov es, ax
    mov bx, [bx]
    pop ds
    pop ax
    iret

s_version:                          # 30: pretend to be DOS 3.0
    mov ax, 3
    xor bx, bx
    xor cx, cx
    iret

s_exit:                             # 4C / INT 20h: AL = exit code
    cld
    xor cx, cx
    mov ds, cx
    mov es, cx
    mov ss, cx
    mov sp, [ksp]                   # back on the kernel stack
    mov [exitcode], al
    sti
    jmp run_done

# ---- data ----
c_help:   .asciz "HELP"
c_ver:    .asciz "VER"
c_cls:    .asciz "CLS"
c_echo:   .asciz "ECHO"
c_mem:    .asciz "MEM"
c_time:   .asciz "TIME"
c_date:   .asciz "DATE"
c_dir:    .asciz "DIR"
c_type:   .asciz "TYPE"
c_reboot: .asciz "REBOOT"
c_run:    .asciz "RUN"

m_prompt: .asciz "A:\\>"
m_crlf:   .asciz "\r\n"
m_bad:    .asciz "Bad command or file name\r\n"
m_usage:  .asciz "Usage: TYPE filename\r\n"
m_runusage: .asciz "Usage: RUN program [arguments]\r\n"
m_big:    .asciz "Program too big\r\n"
m_badprog: .asciz "Bad program\r\n"
m_exitcode: .asciz "Exit code "
m_nofile: .asciz "File not found\r\n"
m_fserr:  .asciz "Disk read error\r\n"
m_nofs:   .asciz "No file system (disk error at boot)\r\n"
m_mem:    .asciz " KB conventional memory\r\n"
m_bytes:  .asciz " bytes\r\n"
m_dirtag: .asciz "<DIR>\r\n"
m_files:  .asciz " file(s)\r\n"
m_dirs:   .asciz " dir(s)\r\n"
m_dirhdr: .asciz " Volume in drive A is MOSFETQ\r\n\r\n"
m_ver:    .asciz "MOSFETQ DOS 0.3 (real mode, FAT12, .COM programs)\r\n"
m_banner: .ascii "MOSFETQ DOS 0.3\r\n"
          .asciz "Type HELP for a list of commands.\r\n\r\n"
m_help:   .ascii "HELP    this list\r\n"
          .ascii "VER     show version\r\n"
          .ascii "CLS     clear the screen\r\n"
          .ascii "ECHO x  print text\r\n"
          .ascii "MEM     conventional memory size\r\n"
          .ascii "TIME    RTC time     DATE   RTC date\r\n"
          .ascii "DIR     list the disk (FAT12 root directory)\r\n"
          .ascii "TYPE f  show a file from the disk\r\n"
          .ascii "RUN p   run p.COM (or just type its name)\r\n"
          .asciz "REBOOT  restart the machine\r\n"

fs_ok:    .byte 0
exitcode: .byte 0
argname:  .word 0
ksp:      .word 0
dcount:   .word 0
dircount: .word 0
rem_lo:   .word 0
rem_hi:   .word 0
chs_cx:   .word 0
chs_dx:   .word 0
namebuf:  .space 16
fcbname:  .space 12
buf:      .space 64
kernel_end:
                                                                                                                                                                                                                                                                                                                                                                                                                                                                   