#include <stdint.h>
#include "vmm.h"
#include "pmm.h"

static inline void outb(unsigned short port, unsigned char val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

void vmm_init() {
    outb(0x3F8, 'V');
    outb(0x3F8, '1');

    uint32_t* page_directory = (uint32_t*) pmm_alloc_page();
    uint32_t* first_page_table = (uint32_t*) pmm_alloc_page();

    outb(0x3F8, 'V');
    outb(0x3F8, '2');

    for (int i = 0; i < 1024; i++) {
        first_page_table[i] = (i * 4096) | 3;
    }

    outb(0x3F8, 'V');
    outb(0x3F8, '3');

    page_directory[0] = ((uint32_t)first_page_table) | 3;

    for (int i = 1; i < 1024; i++) {
        page_directory[i] = 0;
    }

    outb(0x3F8, 'V');
    outb(0x3F8, '4');

    __asm__ volatile (
        "mov %0, %%eax\n\t"
        "mov %%eax, %%cr3\n\t"
        "mov %%cr0, %%eax\n\t"
        "or $0x80000000, %%eax\n\t"
        "mov %%eax, %%cr0\n\t"
        : : "r"(page_directory) : "%eax", "memory"
    );

    outb(0x3F8, 'V');
    outb(0x3F8, '5');

    // Test virtual memory access by reading/writing to a mapped virtual address (e.g., 0xB8000)
    volatile uint32_t* test_ptr = (volatile uint32_t*) 0xB8000;
    uint32_t val = *test_ptr;
    (void)val;

    outb(0x3F8, 'V');
    outb(0x3F8, '6');
}
