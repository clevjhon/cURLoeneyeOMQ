#ifndef MULTIBOOT_H
#define MULTIBOOT_H
#define MULTIBOOT_MAGIC 0x2BADB002
typedef struct {
 unsigned int flags;
 unsigned int mem_lower;
 unsigned int mem_upper;
 unsigned int boot_device;
 unsigned int cmdline;
 unsigned int mods_count;
 unsigned int mods_addr;
 unsigned int syms[4];
 unsigned int mmap_length;
 unsigned int mmap_addr;
 unsigned int drives_length;
 unsigned int drives_addr;
 unsigned int config_table;
 unsigned int boot_loader_name;
 unsigned int apm_table;
 unsigned int vbe_control_info;
 unsigned int vbe_mode_info;
 unsigned short vbe_mode;
 unsigned short vbe_interface_seg;
 unsigned short vbe_interface_off;
 unsigned short vbe_interface_len;
} multiboot_info_t;

typedef struct {
 unsigned int size;
 unsigned long long base_addr;
 unsigned long long length;
 unsigned int type;
} __attribute__((packed)) multiboot_memory_map_t;

// helpers for low 32 bits
#define base_addr_low base_addr
#define length_low length

// Actually use macros to get low part - but we use direct fields below
#undef base_addr_low
#undef length_low
typedef struct {
 unsigned int size;
 unsigned int base_addr_low;
 unsigned int base_addr_high;
 unsigned int length_low;
 unsigned int length_high;
 unsigned int type;
} __attribute__((packed)) multiboot_mmap_compat_t;

#define multiboot_memory_map_t multiboot_mmap_compat_t

#endif
