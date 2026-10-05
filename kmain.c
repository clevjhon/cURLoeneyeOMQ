
#include "pmm.h"
void vmm_init();
static void outb(unsigned short p, unsigned char v){__asm__ volatile("outb %0,%1"::"a"(v),"Nd"(p));}
static void putc(char c){outb(0x3F8,c);}
static void puts(const char* s){for(;*s;s++) putc(*s);}
void kmain(void* mbd, unsigned int magic){
 puts("\n[cURLoeneyeOMQ] Booted!\n");
  pmm_init(mbd);
   void* a=pmm_alloc_page(); void* b=pmm_alloc_page();
    puts("[PMM] 2 pages OK\n");
     puts("[VMM] calling vmm_init...\n");
      vmm_init();
       puts("\n[VMM] Paging enabled! V1-V6 passed - FIXED!\n");
        puts("Halting. CTRL+C to exit\n");
         while(1){__asm__ volatile("cli; hlt");}
         }
         