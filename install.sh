#!/bin/bash
set -e
echo "=============================="
echo " OENEYE ECOSYSTEM INSTALLATION"
echo "=============================="

DB_URL="https://github.com/clevjhon/cURLoeneyeOMQ/releases/download/v1.1/termuxDB.bin"

if [! -f "termuxDB.bin" ]; then
    echo "[+] Downloading DB (311M)..."
    curl -L $DB_URL -o termuxDB.bin --progress-bar
else
    echo "[+] DB exists ($(du -h termuxDB.bin | cut -f1))"
fi

# --- Entropy verification ---
if [ -f "verify_random.py" ]; then
    echo "[+] Verifying DB randomness..."
    python3 verify_random.py termuxDB.bin
else
    echo "[!] verify_random.py missing, skipping check"
fi

mkdir -p brand emulator mosfetq-dos vfat-lfn fat77 docs

if [ -f "index.html" ] && [ -f "OENEYE_EULA.md" ]; then
    echo "[+] Core portal and EULA verified."
else
    echo "[!] Portal files missing, generating..."
    [ -f "oeneye_html_generator.py" ] && python3 oeneye_html_generator.py || echo "[!] generator not found"
fi

echo "[+] Installation complete."
