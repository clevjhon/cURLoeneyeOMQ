#include <cuda_runtime.h>
#include <stdio.h>

#define FAT77_SECTOR_SIZE 512
#define FAT77_MAX_CLUSTERS 65536

struct FAT77Superblock {
    char signature[8]; // "FAT77[o]"
    unsigned int total_clusters;
    unsigned int root_dir_cluster;
};

__global__ void verify_fat77_chain_kernel(const unsigned int* fat_table, unsigned int* validation_results, int max_chains) {
    int idx = blockDim.x * blockIdx.x + threadIdx.x;
    if (idx < max_chains) {
        unsigned int next_cluster = fat_table[idx];
        if (next_cluster == 0x00000000) {
            validation_results[idx] = 0; // Unallocated / Free
        } else if (next_cluster >= 0x0FFFFFF8) {
            validation_results[idx] = 1; // End of Chain (Valid)
        } else {
            validation_results[idx] = 2; // Active Link
        }
    }
}
