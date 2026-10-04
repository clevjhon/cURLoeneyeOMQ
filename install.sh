#!/bin/bash
echo "========================================"
echo "   OENEYE ECOSYSTEM INSTALLATION"
#!/bin/bash
echo "========================================"
echo "  OENEYE ECOSYSTEM INSTALLATION"
echo "========================================"

# --- Download DB if missing ---
DB_URL="https://github.com/clevjhon/cURLoeneyeOMQ/releases/download/v1.0/termuxDB.bin"
if [ ! -f "termuxDB.bin" ]; then
  echo "[+] Downloading DB (311M)..."
  curl -L $DB_URL -o termuxDB.bin --progress-bar
else
  echo "[+] DB already exists"
fi

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
echo "========================================"echo "========================================"

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
