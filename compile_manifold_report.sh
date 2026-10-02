#!/data/data/com.termux/files/usr/bin/bash

BASE_ID="2026-0812-CNNN3-1031-BK00-AK47L"
SOURCE_MANIFEST="manifold_archive_manifest.txt"
OUTPUT_PDF="manifold_maga_report.pdf"

echo "=================================================="
echo " COMPILING MANIFOLD REPORT VIA OENEYEPDF"
echo " TRACK ID: $BASE_ID"
echo "=================================================="

if [ -f ./oeneyepdf ]; then
    ./oeneyepdf "$SOURCE_MANIFEST" "$OUTPUT_PDF" /A4 /BRAND
    echo "Report Compiled Successfully: $OUTPUT_PDF 📄✨"
else
    echo "Error: oeneyepdf utility not located in current directory."
fi
