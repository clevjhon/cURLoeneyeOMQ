#!/bin/bash
echo "--- Starting Unified Pipeline Execution ---"
# Step 3: Compile LaTeX monographs and verify font assets
echo "[*] Step 3: Compiling LaTeX monographs and font assets..."
python3 make_pdf.py || exit 1
pkg install python -y
pip install --upgrade pip
pip install reportlab fonttools requests tqdm
# then run again
cd ~/oeneye
chmod +x pipeline.sh
./pipeline.sh
pip install fontforge || pkg install fontforge -y
pip install brotli zopfli
#!/bin/bash
set -e
echo "--- Starting Unified Pipeline Execution ---"
echo "[*] Step 1: DOS shell audit & git sync..."
python3 emu_dos.py --audit
cd ~/oeneye
pwd
ls -la | cat
find ~ -name "emu_dos.py" 2>/dev/null | head -n 20
find ~ -name "pipeline.sh" 2>/dev/null | head -n 20
#!/bin/bash
echo "--- Starting Unified Pipeline Execution ---"
# Step 3: Compile LaTeX monographs and verify font assets
echo "[*] Step 3: Compiling LaTeX monographs and font assets..."
python3 make_pdf.py || exit 1
cat >.gitignore <<'EOF'
.cache/
.cargo/
__pycache__/
.config/
.bash_history
*.img
*.bin
oeneye_os.img
pipeline.sh
EOF

git status
git add.gitignore make_oeneye.py xima_sync.py socket_table.py ssl_oeneye.py update_canary_db.py
git commit -m "feat: unified pipeline 2026-10-02 - kernel 56b + XIMA STABLE + Socket 128/129 + Canary 25f7625a + sslOENEYE loopback OK [o∞o]"
# use your FINAL fresh token, read -s method
read -s PAT
#!/bin/bash
echo "--- Starting Unified Pipeline Execution ---"
# Step 3: Compile LaTeX monographs and font assets
echo "[*] Step 3: Compiling LaTeX monographs and font assets..."
python3 make_pdf.py || exit 1
