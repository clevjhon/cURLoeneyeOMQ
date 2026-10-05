#!/usr/bin/env bash
set -e

echo "[*] Initializing Automated Pipeline..."

# Step 1: Recombine split backup archives if they exist
if ls termuxDB_part_* 1> /dev/null 2>&1; then
    echo "[+] Recombining split database chunks..."
    cat termuxDB_part_* > termuxDB.bin
else
    echo "[!] No split database parts found."
    exit 1
fi

# Step 力的 Step 2: Run Enthalpy/Entropy Verification
echo "[+] Executing Enthalpy & Entropy boundary verification..."
python3 verify_random.py termuxDB.bin

# Step 3: Archive Integrity Validation (Dry-run test)
echo "[+] Testing archive structure and state vectors..."
tar -ztvf termuxDB.bin > /dev/null 2>&1 && echo "[+] Archive structure is valid." || { echo "[!] Critical: Archive corruption or tachyonic anomaly detected."; exit 1; }

echo "[+] Pipeline execution completed successfully. State vectors nominal."

