# MOSFETQ DOS 0.6 - tiny bootable DOS-style OS (16-bit real mode, x86)
# Stage 1: boot sector with FAT12 BPB, loads the kernel with INT 13h.
# Stage 2: kernel + shell + FAT12 driver (DIR, TYPE, DEL) + write primitives +
#          .COM program loader (RUN / bare name) with a minimal INT 21h.
#
# WRITE SUPPORT (Gold Release Candidate):
#   - write_sector / write_sectors
#   - fat_get / fat_set (updates both FAT copies)
#   - find_free_cluster, free_chain
#   - DEL command (delete file + free clusters)
# 0.5: INT 21h file services (open/read/close/seek, write to console) and a
#      fix for FAT entries that straddle a sector boundary (cluster 341, 1365..).
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
.equ LOADSEG,   0x1010          # .EXE image loads at PSP+10h
.equ BATBUF,    0xE000          # a .BAT file is cached here (max 2048 bytes)
.equ RELBUF,    0xF000          # .EXE relocation table (max 121 entries)
.equ NHAND,     8               # open-file table size (handles 5..12)
.equ HSIZE,     12              # bytes per open-file entry

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
    mov si, offset s_autoexec       # like DOS: run AUTOEXEC.BAT if there is one
    call run_com
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

# write_sector: AX = LBA, ES:BX = source. CF=1 on error. Preserves registers.
write_sector:
    push ax
    push bx
    push cx
    push dx
    push si
    xor dx, dx
    mov cx, SPT
    div cx
    inc dl
    mov cl, dl
    mov dh, al
    and dh, 1
    shr ax, 1
    mov ch, al
    mov [chs_cx], cx
    mov dl, [bootdrv]
    mov [chs_dx], dx
    mov si, 3
ws_try:
    mov cx, [chs_cx]
    mov dx, [chs_dx]
    mov ax, 0x0301
    int 0x13
    jnc ws_ok
    xor ah, ah
    mov dl, [bootdrv]
    int 0x13
    dec si
    jnz ws_try
    stc
    jmp ws_out
ws_ok:
    clc
ws_out:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

write_sectors:
    push ax
    push bx
    push cx
wss_loop:
    call write_sector
    jc wss_out
    inc ax
    add bx, 512
    loop wss_loop
    clc
wss_out:
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

fat_get:
    push bx
    push cx
    mov cx, ax
    mov bx, ax
    shr bx, 1
    add bx, ax
    add bx, FATBUF
    mov ax, [bx]
    test cl, 1
    jz fg_even
    shr ax, 4
    jmp fg_end
fg_even:
    and ax, 0x0FFF
fg_end:
    pop cx
    pop bx
    ret

# fat_set: AX = cluster, DX = 12-bit value. Updates the RAM copy of the FAT and
# writes the affected sector(s) to BOTH FAT copies. An entry whose two bytes
# straddle a sector boundary (offset 511, e.g. cluster 341) touches 2 sectors.
# CF=1 on write error. Preserves all registers.
fat_set:
    push ax
    push bx
    push cx
    push dx
    push si
    mov cx, ax
    mov bx, ax
    shr bx, 1
    add bx, ax
    add bx, FATBUF
    mov ax, [bx]
    test cl, 1
    jnz fs_odd
    and ax, 0xF000
    and dx, 0x0FFF
    or ax, dx
    jmp fs_store
fs_odd:
    and ax, 0x000F
    shl dx, 4
    or ax, dx
fs_store:
    mov [bx], ax
    mov ax, bx
    sub ax, FATBUF                  # byte offset of the word inside the FAT
    mov si, ax
    and si, 511                     # SI = offset inside its sector
    shr ax, 9
    mov cx, ax                      # CX = first FAT sector index
    call fat_flush
    jc fs_done
    cmp si, 511
    jne fs_single                   # entry fits in one sector
    mov ax, cx
    inc ax
    call fat_flush                  # second half lives in the next sector
    jmp fs_done
fs_single:
    clc                             # (CMP above may have set CF)
fs_done:
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
    ret

# fat_flush: AX = FAT sector index (0..FAT_SECT-1): write it to both FAT copies.
fat_flush:
    push ax
    push bx
    push cx
    mov cx, ax
    shl cx, 9
    mov bx, FATBUF
    add bx, cx
    add ax, FAT_LBA
    call write_sector
    jc ffl_out
    add ax, FAT_SECT
    call write_sector
ffl_out:
    pop cx
    pop bx
    pop ax
    ret

find_free_cluster:
    push bx
    push cx
    mov cx, 2
ffc_loop:
    cmp cx, 0xFF0
    jae ffc_none
    mov ax, cx
    call fat_get
    test ax, ax
    jz ffc_found
    inc cx
    jmp ffc_loop
ffc_found:
    mov ax, cx
    jmp ffc_out
ffc_none:
    xor ax, ax
ffc_out:
    pop cx
    pop bx
    ret

free_chain:                         # AX = first cluster; frees the chain. CF=1 on disk error
    push ax
    push dx
fc_loop:
    cmp ax, 2
    jb fc_ok
    cmp ax, 0xFF8
    jae fc_ok
    mov dx, ax
    call fat_next
    push ax
    mov ax, dx
    xor dx, dx
    call fat_set
    pop ax
    jc fc_out                       # (POP keeps CF)
    jmp fc_loop
fc_ok:
    clc
fc_out:
    pop dx
    pop ax
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
    mov di, offset c_del
    call match
    jz do_del
    mov di, offset c_reboot
    call match
    jz do_reboot
    mov di, offset c_run
    call match
    jz do_run
    mov di, offset c_print
    call match
    jz do_print
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
    mov dx, si
    mov di, offset c_off
    call match
    jnz echo_try_on
    call skipsp
    cmp byte ptr [si], 0
    jne echo_txt
    mov byte ptr [echo_off], 1      # ECHO OFF: batch files stop showing their lines
    ret
echo_try_on:
    mov di, offset c_on
    call match
    jnz echo_txt
    call skipsp
    cmp byte ptr [si], 0
    jne echo_txt
    mov byte ptr [echo_off], 0
    ret
echo_txt:
    mov si, dx
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

# del_entry: BX = directory entry (inside ROOTBUF). Frees its cluster chain,
# marks the entry deleted (0xE5) and writes the directory sector. CF=1 on error.
del_entry:
    push ax
    push bx
    push cx
    mov ax, [bx+26]
    call free_chain
    jc de_out
    mov byte ptr [bx], 0xE5
    mov ax, bx
    sub ax, ROOTBUF
    shr ax, 9                       # directory sector index
    mov cx, ax
    shl cx, 9
    add cx, ROOTBUF
    mov bx, cx                      # BX = that sector in RAM
    add ax, ROOT_LBA
    call write_sector
de_out:
    pop cx
    pop bx
    pop ax
    ret

do_del:
    cmp byte ptr [fs_ok], 0
    je no_fs
    call skipsp
    cmp byte ptr [si], 0
    je del_usage
    call make_fcb
    call find_file
    jc del_nf
    test byte ptr [bx+11], 0x18
    jnz del_nf                      # directory / label
    call del_entry
    jc del_err
    mov si, offset m_deleted
    call puts
    ret
del_nf:
    mov si, offset m_nofile
    call puts
    ret
del_err:
    mov si, offset m_fserr
    call puts
    ret
del_usage:
    mov si, offset m_delusage
    call puts
    ret

do_reboot:
    .byte 0xEA
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
# Finds NAME.COM, NAME.EXE or NAME.BAT (or uses the extension typed) and runs it.
# CF=1 if there is no such program; CF=0 if it ran (or an error was printed).
run_com:
    cmp byte ptr [fs_ok], 0
    je rc_nf
    mov [argname], si
    call make_fcb
    cmp byte ptr [fcbname+8], ' '
    jne rc_explicit
    mov si, offset x_com            # no extension typed: try .COM, .EXE, .BAT
    call set_ext
    call find_file
    jnc rc_found
    mov si, offset x_exe
    call set_ext
    call find_file
    jnc rc_found
    mov si, offset x_bat
    call set_ext
    call find_file
    jnc rc_found
    jmp rc_nf
rc_explicit:
    call find_file
    jc rc_nf
rc_found:
    test byte ptr [bx+11], 0x18
    jnz rc_nf                       # directory / label
    mov si, offset x_com
    call ext_is
    je rc_com
    mov si, offset x_exe
    call ext_is
    je rc_exe
    mov si, offset x_bat
    call ext_is
    je rc_bat
    jmp rc_nf

set_ext:                            # SI -> 3 chars: copy into fcbname's extension
    mov al, [si]
    mov [fcbname+8], al
    mov al, [si+1]
    mov [fcbname+9], al
    mov al, [si+2]
    mov [fcbname+10], al
    ret

ext_is:                             # SI -> 3 chars. ZF=1 if fcbname has that extension
    mov al, [si]
    cmp al, [fcbname+8]
    jne ei_ret
    mov al, [si+1]
    cmp al, [fcbname+9]
    jne ei_ret
    mov al, [si+2]
    cmp al, [fcbname+10]
ei_ret:
    ret

# ---- .COM: load the file at 1000:0100 ----
rc_com:
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
    call build_psp                  # (ES = COMSEG)
    mov di, 0xFFFC
    xor ax, ax
    stosw                           # word 0 on the stack: a plain RET -> PSP:0000 = INT 20h
    mov word ptr [l_cs], COMSEG
    mov word ptr [l_ip], 0x0100
    mov word ptr [l_ss], COMSEG
    mov word ptr [l_sp], 0xFFFC
    jmp rc_launch

# ---- .EXE (MZ): header, relocations, image at PSP+10h ----
rc_exe:
    cmp word ptr [bx+30], 0
    jne rc_big
    mov ax, [bx+28]
    cmp ax, 0x40
    jb rc_bad
    cmp ax, MAXCOM
    ja rc_big
    mov [f_size], ax
    mov cx, [bx+26]
    mov [c_clu], cx
    xor ax, ax
    mov es, ax
    mov ax, cx
    add ax, DATA_LBA - 2
    mov bx, FILEBUF
    call read_sector                # sector 0 holds the MZ header
    jc rc_rderr
    cmp word ptr [FILEBUF], 0x5A4D  # 'MZ'
    jne rc_bad
    mov ax, [FILEBUF+8]             # header size in paragraphs
    shl ax, 4
    mov [x_hdr], ax
    cmp ax, [f_size]
    jae rc_bad
    mov ax, [FILEBUF+4]             # file size in 512-byte pages
    cmp ax, 0x78
    ja rx_usefile
    shl ax, 9
    mov bx, [FILEBUF+2]             # bytes used in the last page (0 = all)
    test bx, bx
    jz rx_chk
    sub ax, 512
    add ax, bx
rx_chk:
    cmp ax, [f_size]
    jbe rx_tot
rx_usefile:
    mov ax, [f_size]                # header claims more than the file holds
rx_tot:
    mov [x_total], ax
    cmp ax, [x_hdr]
    jbe rc_bad
    cmp word ptr [FILEBUF+6], 121   # relocation table must fit in sector 0
    ja rc_bad
    mov ax, [FILEBUF+6]
    mov [x_nrel], ax
    shl ax, 2
    add ax, [FILEBUF+24]
    cmp ax, 512
    ja rc_bad
    mov ax, [x_total]               # LOADSEG + image + minalloc must fit below A000:0
    sub ax, [x_hdr]
    add ax, 15
    shr ax, 4
    add ax, [FILEBUF+10]
    jc rc_big
    add ax, LOADSEG
    jc rc_big
    cmp ax, 0xA000
    ja rc_big
    mov cx, [x_nrel]                # keep the relocation table (FILEBUF is reused)
    shl cx, 2
    mov si, [FILEBUF+24]
    add si, FILEBUF
    mov di, RELBUF
    rep movsb
    mov ax, [FILEBUF+22]            # entry point and stack (segments are relative)
    add ax, LOADSEG
    mov [l_cs], ax
    mov ax, [FILEBUF+20]
    mov [l_ip], ax
    mov ax, [FILEBUF+14]
    add ax, LOADSEG
    mov [l_ss], ax
    mov ax, [FILEBUF+16]
    mov [l_sp], ax
    mov word ptr [x_dseg], LOADSEG
    mov word ptr [x_doff], 0
    mov cx, [c_clu]
    xor dx, dx                      # DX = file offset of the current sector
lx_sec:
    cmp cx, 2
    jb lx_done
    cmp cx, 0xFF8
    jae lx_done
    cmp dx, [x_total]
    jae lx_done
    xor ax, ax
    mov es, ax
    mov ax, cx
    add ax, DATA_LBA - 2
    mov bx, FILEBUF
    call read_sector
    jc rc_rderr
    mov bx, [x_hdr]
    sub bx, dx
    jae lx_hd                       # the header ends in or after this sector
    xor bx, bx                      # header is over: copy from the sector start
    jmp lx_s
lx_hd:
    cmp bx, 512
    jae lx_next                     # the whole sector is header
lx_s:
    mov ax, [x_total]
    sub ax, dx                      # file bytes left from here
    cmp ax, 512
    jbe lx_e
    mov ax, 512
lx_e:
    sub ax, bx                      # count = end - start
    jbe lx_next
    push cx
    push dx
    mov cx, ax
    mov si, FILEBUF
    add si, bx
    mov di, [x_doff]
    mov ax, [x_dseg]
    mov es, ax
    rep movsb
    mov ax, di
    shr ax, 4                       # keep the destination offset below 16
    add [x_dseg], ax
    and di, 15
    mov [x_doff], di
    pop dx
    pop cx
lx_next:
    add dx, 512
    mov ax, cx
    call fat_next
    mov cx, ax
    jmp lx_sec
lx_done:
    xor ax, ax
    mov es, ax
    mov cx, [x_nrel]                # apply relocations: word += LOADSEG
    mov si, RELBUF
    mov bx, LOADSEG
rx_rel:
    test cx, cx
    jz rx_reldone
    lodsw
    mov di, ax                      # offset
    lodsw                           # segment (relative)
    add ax, bx
    jc rc_bad
    cmp ax, 0xA000
    jae rc_bad
    mov ds, ax
    add [di], bx
    xor ax, ax
    mov ds, ax
    dec cx
    jmp rx_rel
rx_reldone:
    mov ax, COMSEG
    mov es, ax
    call build_psp
    jmp rc_launch

# ---- .BAT: cache the file, then feed its lines to the shell ----
rc_bat:
    cmp byte ptr [bat_busy], 0
    jne rc_nest
    cmp word ptr [bx+30], 0
    jne rc_big
    mov ax, [bx+28]
    cmp ax, 2048
    ja rc_big
    mov [bat_len], ax
    test ax, ax
    jz rb_none
    mov cx, [bx+26]
    mov bx, BATBUF
rb_rd:
    cmp cx, 2
    jb rb_rdone
    cmp cx, 0xFF8
    jae rb_rdone
    cmp bx, BATBUF + 2048
    jae rb_rdone
    mov ax, cx
    add ax, DATA_LBA - 2
    call read_sector
    jc rc_rderr
    add bx, 512
    mov ax, cx
    call fat_next
    mov cx, ax
    jmp rb_rd
rb_rdone:
    mov ax, BATBUF
    mov [bat_pos], ax
    add ax, [bat_len]
    mov [bat_end], ax
    mov byte ptr [bat_busy], 1
rb_line:
    mov si, [bat_pos]
    cmp si, [bat_end]
    jae rb_end
    mov di, offset buf
    xor cx, cx
rb_ch:
    cmp si, [bat_end]
    jae rb_eol
    mov al, [si]
    inc si
    cmp al, 0x0D
    je rb_eol
    cmp al, 0x0A
    je rb_eol
    cmp cx, 63
    jae rb_ch                       # over-long line: drop the excess
    stosb
    inc cx
    jmp rb_ch
rb_eol:
    xor al, al
    stosb
    mov [bat_pos], si
    call bat_line
    jmp rb_line
rb_end:
    mov byte ptr [bat_busy], 0
    mov byte ptr [echo_off], 0
rb_none:
    clc
    ret
rc_nest:
    mov si, offset m_nest
    jmp rc_errmsg

# bat_line: one line of a batch file is in buf. '@' hides it, REM / :label are skipped.
bat_line:
    mov byte ptr [bat_quiet], 0
    mov si, offset buf
    cmp byte ptr [si], '@'
    jne bl_a
    mov byte ptr [bat_quiet], 1
    inc si
bl_a:
    call skipsp
    mov di, offset buf
bl_sh:
    lodsb
    stosb
    test al, al
    jnz bl_sh
    cmp byte ptr [buf], 0
    je bl_ret
    cmp byte ptr [buf], ':'
    je bl_ret
    mov si, offset buf
    mov di, offset c_rem
    call match
    jz bl_ret
    cmp byte ptr [echo_off], 0
    jne bl_run
    cmp byte ptr [bat_quiet], 0
    jne bl_run
    mov si, offset m_prompt
    call puts
    mov si, offset buf
    call puts
    call crlf
bl_run:
    call dispatch
bl_ret:
    ret

# build_psp: ES = COMSEG. Builds the Program Segment Prefix with the command tail.
build_psp:
    cld
    xor di, di
    xor ax, ax
    mov cx, 128
    rep stosw                       # zero 1000:0000-00FF
    xor di, di
    mov ax, 0x20CD                  # PSP:0000 = INT 20h
    stosw
    mov ax, 0xA000                  # PSP:0002 = top of memory segment
    stosw
    mov si, [argname]
bp_tok:                             # skip the program name
    mov al, [si]
    test al, al
    jz bp_noargs
    cmp al, ' '
    je bp_gotsp
    inc si
    jmp bp_tok
bp_gotsp:
    call skipsp
    cmp byte ptr [si], 0
    je bp_noargs
    mov di, 0x81                    # command tail: " args" CR, length at 0x80
    mov al, ' '
    stosb
    mov cx, 1
bp_cp:
    lodsb
    test al, al
    jz bp_cpdone
    stosb
    inc cx
    cmp cx, 120
    jb bp_cp
bp_cpdone:
    mov al, 13
    stosb
    mov di, 0x80
    mov al, cl
    stosb
    ret
bp_noargs:
    mov di, 0x81
    mov al, 13
    stosb
    ret

# rc_launch: start the program described by l_cs:l_ip and l_ss:l_sp
rc_launch:
    xor ax, ax
    mov es, ax
    mov di, offset htab             # every program starts with no open files
    mov cx, NHAND * HSIZE / 2
    rep stosw
    mov [ksp], sp                   # INT 20h / 21h-4Ch come back here
    mov ax, [l_ip]
    mov [jip], ax
    mov ax, [l_cs]
    mov [jcs], ax
    mov cx, [l_ss]
    mov dx, [l_sp]
    mov ax, COMSEG
    mov ds, ax                      # DS = ES = PSP segment
    mov es, ax
    mov ss, cx
    mov sp, dx
    xor ax, ax
    xor bx, bx
    mov cx, 0x00FF
    xor dx, dx
    xor si, si
    xor di, di
    xor bp, bp
    jmp jstub
jstub:
    .byte 0xEA                      # jmp far jcs:jip (operands patched above)
jip:
    .word 0
jcs:
    .word 0

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
    mov ds, ax
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
    cmp ah, 0x05
    je s_prn
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
    cmp ah, 0x3D
    je s_open
    cmp ah, 0x3E
    je s_close
    cmp ah, 0x3F
    je s_read
    cmp ah, 0x40
    je s_write
    cmp ah, 0x42
    je s_seek
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

# ---------------------------------------------------------------- FILE SERVICES
# INT 21h 3Dh open / 3Eh close / 3Fh read / 40h write (console only) / 42h seek.
# Handles 0-4 are the standard devices; files get handles 5..12.
# Open-file entry (HSIZE=12): +0 in-use, +2 first cluster, +4 size (32-bit),
#                             +8 position (32-bit).
# Services run on the program's stack with a saved frame; DS=ES=0 inside.
.macro KENTER
    push ax
    push bp
    push si
    push di
    push bx
    push cx
    push dx
    push ds
    push es
    mov bp, sp                      # [bp+0]=ES +2=DS +4=DX +6=CX +8=BX +10=DI
    xor ax, ax                      # +12=SI +14=BP +16=AX +18=IP +20=CS +22=FLAGS
    mov ds, ax
    mov es, ax
    cld
.endm

.macro KLEAVE
    pop es
    pop ds
    pop dx
    pop cx
    pop bx
    pop di
    pop si
    pop bp
    pop ax
    iret
.endm

k_ok:                               # AX = result, CF=0
    mov [bp+16], ax
    and word ptr [bp+22], 0xFFFE
    KLEAVE
k_err:                              # AX = DOS error code, CF=1
    mov [bp+16], ax
    or word ptr [bp+22], 1
    KLEAVE
k_badh:
    mov ax, 6                       # invalid handle
    jmp k_err

# h_lookup: AX = handle -> DI = table entry. CF=1 if invalid/closed.
h_lookup:
    sub ax, 5
    jb hl_bad
    cmp ax, NHAND
    jae hl_bad
    mov di, ax
    shl di, 2
    shl ax, 3
    add di, ax                      # DI = index * 12
    add di, offset htab
    cmp word ptr [di], 0
    je hl_bad
    clc
    ret
hl_bad:
    stc
    ret

s_open:                             # AL = mode, DS:DX = "NAME.EXT" -> AX = handle
    KENTER
    test byte ptr [bp+16], 7        # only read access (mode 0) exists yet
    jnz so_denied
    mov si, [bp+4]
    mov ds, [bp+2]                  # DS:SI = program's file name
    mov di, offset pathbuf
    mov cx, 64
so_copy:
    lodsb
    stosb                           # ES:DI = kernel buffer
    test al, al
    jz so_copied
    loop so_copy
    xor al, al
    stosb
so_copied:
    xor ax, ax
    mov ds, ax
    mov si, offset pathbuf
    cmp byte ptr [si+1], ':'
    jne so_nodrive
    add si, 2                       # skip "A:"
so_nodrive:
    cmp byte ptr [si], '\\'
    je so_skip
    cmp byte ptr [si], '/'
    jne so_name
so_skip:
    inc si
so_name:
    call make_fcb
    call find_file
    jc so_nf
    test byte ptr [bx+11], 0x18
    jnz so_nf                       # directory / label
    mov di, offset htab
    mov cx, NHAND
so_slot:
    cmp word ptr [di], 0
    je so_free
    add di, HSIZE
    loop so_slot
    mov ax, 4                       # too many open files
    jmp k_err
so_free:
    mov word ptr [di], 1
    mov ax, [bx+26]
    mov [di+2], ax
    mov ax, [bx+28]
    mov [di+4], ax
    mov ax, [bx+30]
    mov [di+6], ax
    xor ax, ax
    mov [di+8], ax
    mov [di+10], ax
    mov ax, NHAND + 5
    sub ax, cx                      # handle = 5 + slot index
    jmp k_ok
so_nf:
    mov ax, 2                       # file not found
    jmp k_err
so_denied:
    mov ax, 5                       # access denied
    jmp k_err

s_close:                            # BX = handle
    KENTER
    mov ax, [bp+8]
    call h_lookup
    jc k_badh
    mov word ptr [di], 0
    xor ax, ax
    jmp k_ok

s_read:                             # BX = handle, CX = count, DS:DX = buffer -> AX = bytes read
    KENTER
    mov ax, [bp+8]
    call h_lookup
    jc k_badh
    mov si, di                      # SI = open-file entry
    mov cx, [bp+6]                  # CX = bytes wanted, limited to size - position
    mov ax, [si+4]
    mov dx, [si+6]
    sub ax, [si+8]
    sbb dx, [si+10]
    jb sr_none                      # position is past the end
    test dx, dx
    jnz sr_lim
    cmp ax, cx
    jae sr_lim
    mov cx, ax
sr_lim:
    mov [r_left], cx
    mov word ptr [r_total], 0
    mov ax, [bp+4]
    mov [r_off], ax
sr_loop:
    cmp word ptr [r_left], 0
    je sr_done
    mov ax, [si+8]                  # cluster index = position / 512
    shr ax, 9
    mov dx, [si+10]
    shl dx, 7
    or ax, dx
    mov cx, ax
    mov ax, [si+2]                  # walk the chain from the first cluster
sr_walk:
    cmp ax, 2
    jb sr_done
    cmp ax, 0xFF8
    jae sr_done                     # chain ended early (corrupt FAT): stop
    test cx, cx
    jz sr_have
    call fat_next
    dec cx
    jmp sr_walk
sr_have:
    add ax, DATA_LBA - 2
    mov bx, FILEBUF
    call read_sector
    jc sr_ioerr
    mov dx, [si+8]
    and dx, 511                     # DX = offset inside the sector
    mov cx, 512
    sub cx, dx
    cmp cx, [r_left]
    jbe sr_chunk
    mov cx, [r_left]
sr_chunk:                           # copy CX bytes FILEBUF+DX -> program buffer
    push si
    mov si, FILEBUF
    add si, dx
    mov di, [r_off]
    mov ax, [bp+2]
    mov es, ax                      # ES = program segment
    mov dx, cx
    rep movsb
    xor ax, ax
    mov es, ax
    pop si
    add [r_off], dx
    add [r_total], dx
    sub [r_left], dx
    add [si+8], dx
    adc word ptr [si+10], 0
    jmp sr_loop
sr_done:
    mov ax, [r_total]
    jmp k_ok
sr_none:
    xor ax, ax
    jmp k_ok
sr_ioerr:
    mov ax, 0x1E                    # read fault
    jmp k_err

s_write:                            # BX = handle, CX = count, DS:DX = data (console only)
    KENTER
    mov ax, [bp+8]
    cmp ax, 1
    je sw_con
    cmp ax, 2
    je sw_con
    cmp ax, 4
    je sw_prn                       # handle 4 = PRN (LPT1)
    call h_lookup
    jc k_badh
    mov ax, 5                       # files are read-only for now
    jmp k_err
sw_con:
    mov cx, [bp+6]
    mov si, [bp+4]
    mov ds, [bp+2]
sw_loop:
    test cx, cx
    jz sw_done
    lodsb
    call putc
    dec cx
    jmp sw_loop
sw_done:
    xor ax, ax
    mov ds, ax
    mov ax, [bp+6]
    jmp k_ok

sw_prn:
    mov cx, [bp+6]
    mov si, [bp+4]
    mov ds, [bp+2]
wp_loop:
    test cx, cx
    jz wp_done
    lodsb
    call lpt_putc
    jc wp_err
    dec cx
    jmp wp_loop
wp_err:
    xor ax, ax
    mov ds, ax
    mov ax, 0x1D                    # write fault (printer not ready)
    jmp k_err
wp_done:
    xor ax, ax
    mov ds, ax
    mov ax, [bp+6]
    jmp k_ok

s_prn:                              # 05: send DL to the printer (LPT1)
    push ax
    push dx
    mov al, dl
    xor ah, ah
    xor dx, dx
    int 0x17
    pop dx
    pop ax
    iret

s_seek:                             # AL = origin, BX = handle, CX:DX = offset -> DX:AX
    KENTER
    mov ax, [bp+8]
    call h_lookup
    jc k_badh
    mov si, di
    mov al, [bp+16]
    mov cx, [bp+6]
    mov dx, [bp+4]
    cmp al, 0
    je ss_start
    cmp al, 1
    je ss_cur
    cmp al, 2
    je ss_end
    mov ax, 1                       # invalid origin
    jmp k_err
ss_start:
    xor ax, ax
    xor bx, bx
    jmp ss_calc
ss_cur:
    mov ax, [si+8]
    mov bx, [si+10]
    jmp ss_calc
ss_end:
    mov ax, [si+4]
    mov bx, [si+6]
ss_calc:
    add ax, dx
    adc bx, cx
    test bx, 0x8000
    jnz ss_bad                      # before the start of the file
    mov [si+8], ax
    mov [si+10], bx
    mov [bp+4], bx                  # return DX = high word, AX = low word
    jmp k_ok
ss_bad:
    mov ax, 0x19                    # seek error
    jmp k_err

# ================================================================ PRINTER / PLOTTER
# lpt_putc: AL -> LPT1 through BIOS INT 17h. CF=1 if the printer reports
# timeout, I/O error or out of paper. Preserves all registers.
lpt_putc:
    push ax
    push dx
    xor ah, ah
    xor dx, dx
    int 0x17
    test ah, 0x29
    pop dx
    pop ax
    jnz lp_err                      # (POP keeps the flags from TEST)
    clc
    ret
lp_err:
    stc
    ret

# PRINT filename: send the file, byte for byte, to LPT1. Works for text and for
# plotter files (HPGL) alike - nothing is translated.
do_print:
    cmp byte ptr [fs_ok], 0
    je no_fs
    call skipsp
    cmp byte ptr [si], 0
    je print_usage
    call make_fcb
    call find_file
    jc print_nf
    test byte ptr [bx+11], 0x18
    jnz print_nf
    mov cx, [bx+26]
    mov ax, [bx+28]
    mov [rem_lo], ax
    mov [psz_lo], ax
    mov ax, [bx+30]
    mov [rem_hi], ax
    mov [psz_hi], ax
pr_loop:
    cmp cx, 2
    jb pr_done
    cmp cx, 0xFF8
    jae pr_done
    mov ax, [rem_lo]
    or ax, [rem_hi]
    jz pr_done
    mov ax, cx
    add ax, DATA_LBA - 2
    mov bx, FILEBUF
    call read_sector
    jc pr_rderr
    mov ax, 512
    cmp word ptr [rem_hi], 0
    jne pr_n
    cmp word ptr [rem_lo], 512
    jae pr_n
    mov ax, [rem_lo]
pr_n:
    sub [rem_lo], ax
    sbb word ptr [rem_hi], 0
    push cx
    mov cx, ax
    mov si, FILEBUF
pr_byte:
    test cx, cx
    jz pr_bdone
    lodsb
    call lpt_putc
    jc pr_prnerr
    dec cx
    jmp pr_byte
pr_bdone:
    pop cx
    mov ax, cx
    call fat_next
    mov cx, ax
    jmp pr_loop
pr_prnerr:
    pop cx
    mov si, offset m_prnerr
    call puts
    ret
pr_done:
    mov ax, [psz_lo]                # bytes sent = size - what is left
    mov dx, [psz_hi]
    sub ax, [rem_lo]
    sbb dx, [rem_hi]
    call print_dec32
    mov si, offset m_sent
    call puts
    ret
pr_rderr:
    mov si, offset m_fserr
    call puts
    ret
print_nf:
    mov si, offset m_nofile
    call puts
    ret
print_usage:
    mov si, offset m_printusage
    call puts
    ret

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
c_print:  .asciz "PRINT"
c_rem:    .asciz "REM"
c_on:     .asciz "ON"
c_off:    .asciz "OFF"
x_com:    .ascii "COM"
x_exe:    .ascii "EXE"
x_bat:    .ascii "BAT"
s_autoexec: .asciz "AUTOEXEC.BAT"
c_del:    .asciz "DEL"

m_prompt: .asciz "A:\\>"
m_crlf:   .asciz "\r\n"
m_bad:    .asciz "Bad command or file name\r\n"
m_usage:  .asciz "Usage: TYPE filename\r\n"
m_runusage: .asciz "Usage: RUN program [arguments]\r\n"
m_big:    .asciz "Program too big\r\n"
m_prnerr: .asciz "Printer not ready\r\n"
m_sent:   .asciz " bytes sent to LPT1\r\n"
m_printusage: .asciz "Usage: PRINT filename\r\n"
m_nest:   .asciz "Batch files cannot be nested\r\n"
m_badprog: .asciz "Bad program\r\n"
m_exitcode: .asciz "Exit code "
m_nofile: .asciz "File not found\r\n"
m_fserr:  .asciz "Disk error\r\n"
m_deleted:.asciz "File deleted\r\n"
m_delusage: .asciz "Usage: DEL filename\r\n"
m_nofs:   .asciz "No file system (disk error at boot)\r\n"
m_mem:    .asciz " KB conventional memory\r\n"
m_bytes:  .asciz " bytes\r\n"
m_dirtag: .asciz "<DIR>\r\n"
m_files:  .asciz " file(s)\r\n"
m_dirs:   .asciz " dir(s)\r\n"
m_dirhdr: .asciz " Volume in drive A is MOSFETQ\r\n\r\n"
m_ver:    .asciz "MOSFETQ DOS 0.6 (real mode, FAT12, .COM/.EXE/.BAT, AUTOEXEC)\r\n"
m_banner: .ascii "MOSFETQ DOS 0.6\r\n"
          .asciz "Type HELP for a list of commands.\r\n\r\n"
m_help:   .ascii "HELP    this list\r\n"
          .ascii "VER     show version\r\n"
          .ascii "CLS     clear the screen\r\n"
          .ascii "ECHO x  print text\r\n"
          .ascii "MEM     conventional memory size\r\n"
          .ascii "TIME    RTC time     DATE   RTC date\r\n"
          .ascii "DIR     list the disk (FAT12 root directory)\r\n"
          .ascii "TYPE f  show a file from the disk\r\n"
          .ascii "PRINT f send a file to LPT1 (text or HPGL plot)\r\n"
          .ascii "DEL f   delete a file (write support)\r\n"
          .ascii "RUN p   run p.COM/.EXE/.BAT (or just type its name)\r\n"
          .asciz "REBOOT  restart the machine\r\n"

fs_ok:    .byte 0
echo_off: .byte 0
bat_busy: .byte 0
bat_quiet: .byte 0
bat_pos:  .word 0
bat_end:  .word 0
bat_len:  .word 0
l_cs:     .word 0
l_ip:     .word 0
l_ss:     .word 0
l_sp:     .word 0
f_size:   .word 0
c_clu:    .word 0
x_hdr:    .word 0
x_total:  .word 0
x_nrel:   .word 0
x_dseg:   .word 0
x_doff:   .word 0
exitcode: .byte 0
argname:  .word 0
ksp:      .word 0
dcount:   .word 0
dircount: .word 0
rem_lo:   .word 0
psz_lo:   .word 0
psz_hi:   .word 0
rem_hi:   .word 0
chs_cx:   .word 0
chs_dx:   .word 0
r_left:   .word 0
r_total:  .word 0
r_off:    .word 0
htab:     .space NHAND * HSIZE
pathbuf:  .space 66
namebuf:  .space 16
fcbname:  .space 12
buf:      .space 64
kernel_end:
