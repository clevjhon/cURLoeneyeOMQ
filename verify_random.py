#!/usr/bin/env python3
import sys
import math

def check_enthalpy_and_entropy(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    file_size = len(data)
    if file_size == 0:
        print("[!] Critical State Error: Zero-mass anomaly detected.")
        sys.exit(1)

    frequencies = [data.count(b) / file_size for b in set(data)]
    entropy = -sum(p * math.log2(p) for p in frequencies)
    randomness_score = (entropy / 8.0) * 100

    print(f"--- Enthalpy-Entropy State Analysis ---")
    print(f"Payload Size: {file_size} bytes")
    print(f"Shannon Entropy: {entropy:.4f} bits/byte (Max: 8.0)")
    print(f"Randomness Index: {randomness_score:.2f}%")

    if randomness_score < 50.0:
        print("[!] Tachyonic Instability Warning: Low randomness detected. Aborting extraction.")
        sys.exit(1)
    else:
        print("[+] State Stable: Enthalpy within nominal operational limits.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_enthalpy_and_entropy(sys.argv[1])
    else:
        print("Usage: python3 verify_random.py <archive_path>")

