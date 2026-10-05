static unsigned int bm[1024];
void pmm_init(void* m){for(int i=0;i<1024;i++)bm[i]=0;for(int i=0;i<1024;i++)bm[i>>5]|=1u<<(i&31);}
void* pmm_alloc_page(){for(int i=1024;i<32768;i++)if(!(bm[i>>5]&(1u<<(i&31)))){bm[i>>5]|=1u<<(i&31);return(void*)(i*4096);}return 0;}
