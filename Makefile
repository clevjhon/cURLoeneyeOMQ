CC=clang
TARGET=i386-pc-none-elf
CFLAGS=-ffreestanding -nostdlib -m32 -O0 -mno-sse -mno-sse2 -mno-mmx
LDFLAGS=-T linker.ld -m elf_i386 -nostdlib
OBJS=loader.o kmain.o pmm.o vmm.o
all: kernel.elf
%.o: %.s
	$(CC) --target=$(TARGET) $(CFLAGS) -c $< -o $@
%.o: %.c
	$(CC) --target=$(TARGET) $(CFLAGS) -c $< -o $@
kernel.elf: $(OBJS)
	ld.lld $(LDFLAGS) -o $@ $^
	@echo Built OK!
clean:
	rm -f *.o *.elf
run:
	qemu-system-i386 -kernel kernel.elf -display none -serial stdio -m 128 -no-reboot
