#!/bin/bash
echo "[*] Starting cURLoeneyeOMQ auto-sync with GitHub..."

# Add any modified or new files (like main.py, OMQ.FNT, or text exports)
git add .

# Prompt for a quick commit message, or use a default one
read -p "Enter commit message (press Enter for 'Auto-sync update'): " msg
msg=${msg:-"Auto-sync update"}

git commit -m "$msg"

# Push to your main branch
git branch -M main
git push -u origin main

echo "[*] Sync complete!"

