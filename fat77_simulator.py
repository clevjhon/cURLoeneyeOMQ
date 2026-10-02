#!/usr/bin/env python3

def verify_fat77_chain_simulator(max_chains=1024):
    print(f"[*] Initializing oeneyeOS FAT77 Simulator on Device 0 [0:0] [o∞o]")
    
    fat_table = [0] * max_chains
    for i in range(max_chains):
        if i % 10 == 0:
            fat_table[i] = 0x00000000         # Free cluster
        elif i % 5 == 0:
            fat_table[i] = 0x0FFFFFFF         # End of chain
        else:
            fat_table[i] = i + 1              # Active link

    validation_results = [0] * max_chains
    free_count = 0
    eof_count = 0
    active_count = 0

    for i in range(max_chains):
        val = fat_table[i]
        if val == 0x00000000:
            validation_results[i] = 0
            free_count += 1
        elif val >= 0x0FFFFFF8:
            validation_results[i] = 1
            eof_count += 1
        else:
            validation_results[i] = 2
            active_count += 1

    print("[+] FAT77 Validation Table Verified [o∞o]:")
    print(f"    - Free Clusters: {free_count}")
    print(f"    - End of Chains: {eof_count}")
    print(f"    - Active Links:  {active_count}")

if __name__ == "__main__":
    verify_fat77_chain_simulator()
