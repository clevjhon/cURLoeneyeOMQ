#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>

// Forward declaration of the CUDA kernel
__global__ void verify_fat77_chain_kernel(const unsigned int* fat_table, unsigned int* validation_results, int max_chains);

int main() {
    int device_id = 0;
    
    // Bind to CUDA Device 0 (0:0)
    cudaError_t err = cudaSetDevice(device_id);
    if (err != cudaSuccess) {
        fprintf(stderr, "[!] Failed to set CUDA device %d: %s\n", device_id, cudaGetErrorString(err));
        return 1;
    }
    printf("[+] Bound execution context to CUDA Device %d [0:0] [o∞o]\n", device_id);

    int max_chains = 1024;
    size_t bytes = max_chains * sizeof(unsigned int);

    // Allocate host memory
    unsigned int* h_fat_table = (unsigned int*)malloc(bytes);
    unsigned int* h_results = (unsigned int*)malloc(bytes);

    // Populate mock FAT77 cluster entries
    for (int i = 0; i < max_chains; i++) {
        if (i % 10 == 0) h_fat_table[i] = 0x00000000;          // Free cluster
        else if (i % 5 == 0) h_fat_table[i] = 0x0FFFFFFF;     // End of chain
        else h_fat_table[i] = i + 1;                          // Active link
    }

    // Allocate device memory
    unsigned int *d_fat_table, *d_results;
    cudaMalloc(&d_fat_table, bytes);
    cudaMalloc(&d_results, bytes);

    // Transfer cluster table to GPU Device 0
    cudaMemcpy(d_fat_table, h_fat_table, bytes, cudaMemcpyHostToDevice);

    // Configure kernel execution dimensions
    int threads_per_block = 256;
    int blocks = (max_chains + threads_per_block - 1) / threads_per_block;

    printf("[*] Launching parallel FAT77 verification kernel on Device 0...\n");
    verify_fat77_chain_kernel<<<blocks, threads_per_block>>>(d_fat_table, d_results, max_chains);
    cudaDeviceSynchronize();

    // Copy validation results back to host
    cudaMemcpy(h_results, d_results, bytes, cudaMemcpyDeviceToHost);

    // Tally results
    int free_count = 0, eof_count = 0, active_count = 0;
    for (int i = 0; i < max_chains; i++) {
        if (h_results[i] == 0) free_count++;
        else if (h_results[i] == 1) eof_count++;
        else if (h_results[i] == 2) active_count++;
    }

    printf("[+] FAT77 Validation Table Verified [o∞o]:\n");
    printf("    - Free Clusters: %d\n", free_count);
    printf("    - End of Chains: %d\n", eof_count);
    printf("    - Active Links:  %d\n", active_count);

    // Cleanup resources
    free(h_fat_table);
    free(h_results);
    cudaFree(d_fat_table);
    cudaFree(d_results);

    return 0;
}
