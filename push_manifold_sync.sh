#!/data/data/com.termux/files/usr/bin/bash

# Parameters & Identifiers
BASE_ID="2026-0812-CNNN3-1031-BK00-AK47L"
BRANCH_NAME="main"

echo "=================================================="
echo " SYNCHRONIZING MANIFOLD ASSETS TO GITHUB"
echo " TRACK ID: $BASE_ID"
echo "=================================================="

# 1. Check git status
git status

# 2. Add modified manifold and checksum files
git add manifold_archive_manifest.txt 86_dos_v0.1_original.img maga_post.html truth_post.html

# 3. Commit with tracking ID context
git commit -m "chore(manifold): sync assets and verification manifest for $BASE_ID"

# 4. Push to remote protected branch
git push origin "$BRANCH_NAME"

echo "Sync Complete: Manifold assets pushed successfully! 🚀"
