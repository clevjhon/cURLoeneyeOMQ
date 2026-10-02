#!/bin/bash
echo "========================================"
echo "   OENEYE ECOSYSTEM INSTALLATION"
echo "========================================"

# Ensure required directories exist
mkdir -p brand emulator mosfetq-dos vfat-lfn fat77 docs

# Verify local files
if [ -f "index.html" ] && [ -f "OENEYE_EULA.md" ]; then
    echo "[+] Core portal and EULA verified."
else
    echo "[!] Warning: Portal files missing. Running generators..."
    python3 oeneye_html_generator.py
fi

echo "[+] Installation sequence complete."
echo "========================================"
