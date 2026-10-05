
import os
open("loader.s","w").write(""".set MAGIC, 0x1BADB002
.set FLAGS, 3
.set CHECKSUM, -(MAGIC+FLAGS)
.section .multiboot
.align 4
.long MAGIC
.long FLAGS
.long CHECKSUM
.section .bss
.align 16
stack_bottom:
.skip 16384
stack_top:
.section .text
.global _start
_start:
 mov $stack_top, %esp
 and $0xFFFFFFF0, %esp
 push %eax
 push %ebx
 call kmain
 cli
1: hlt
 jmp 1b
""")
open("linker.ld","w").write("""ENTRY(_start)
SECTIONS{
 . = 0x00100000;
 .multiboot : { *(.multiboot) }
 .text : { *(.text) }
 .rodata : { *(.rodata) }
 .data : { *(.data) }
 .bss : { *(.bss) }
 _kernel_end = .;
}
""")
open("pmm.h","w").write("#ifndef PMM_H\n#define PMM_H\nvoid pmm_init(void* m);\nvoid* pmm_alloc_page();\n#endif\n")
open("pmm.c","w").write("static unsigned int bm[1024];\nvoid pmm_init(void* m){for(int i=0;i<1024;i++)bm[i]=0;for(int i=0;i<1024;i++)bm[i>>5]|=1u<<(i&31);}\nvoid* pmm_alloc_page(){for(int i=1024;i<32768;i++)if(!(bm[i>>5]&(1u<<(i&31)))){bm[i>>5]|=1u<<(i&31);return(void*)(i*4096);}return 0;}\n")
open("kmain.c","w").write('#include "pmm.h"\nstatic void outb(unsigned short p, unsigned char v){__asm__ volatile("outb %0,%1"::"a"(v),"Nd"(p));}\nstatic void putc(char c){outb(0x3F8,c);}\nstatic void puts(const char* s){for(;*s;s++)putc(*s);}\nvoid kmain(void* mbd, unsigned int magic){\n puts("\\n[cURLoeneyeOMQ] Booted! magic OK\\n");\n puts("[PMM] initing...\\n");\n pmm_init(mbd);\n puts("[PMM] inited - 0-4MB reserved\\n");\n void* a=pmm_alloc_page(); void* b=pmm_alloc_page();\n if(a&&b) puts("[PMM] alloc 2 pages OK - FIXED!\\n");\n puts("Halting. CTRL+C to exit\\n");\n while(1){__asm__ volatile("cli; hlt");}\n}\n')
open("vmm.c","w").write("void vmm_init(){}\n")
open("Makefile","w").write("CC=clang\nTARGET=i386-pc-none-elf\nCFLAGS=-ffreestanding -nostdlib -m32 -O0 -mno-sse -mno-sse2 -mno-mmx\nLDFLAGS=-T linker.ld -m elf_i386 -nostdlib\nOBJS=loader.o kmain.o pmm.o vmm.o\nall: kernel.elf\n%.o: %.s\n\t$(CC) --target=$(TARGET) $(CFLAGS) -c $< -o $@\n%.o: %.c\n\t$(CC) --target=$(TARGET) $(CFLAGS) -c $< -o $@\nkernel.elf: $(OBJS)\n\tld.lld $(LDFLAGS) -o $@ $^\n\t@echo Built OK!\nclean:\n\trm -f *.o *.elf\nrun:\n\tqemu-system-i386 -kernel kernel.elf -display none -serial stdio -m 128 -no-reboot\n")
print("fixed - now run make clean && make && make run")
