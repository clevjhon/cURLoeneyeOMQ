#!/data/data/com.termux/files/usr/bin/bash

# Parameters & Identifiers
BASE_ID="2026-0812-CNNN3-1031-BK00-AK47L"
TARGET_URL="https://truthsocial.com/@trumpeneficiaro"
OUTPUT_HTML="trump_profile.html"
OUTPUT_TXT="trump_profile_source.txt"
OUTPUT_PDF="trump_beneficiaro_profile.pdf"

echo "=================================================="
echo " FETCHING TRUTH SOCIAL ACCOUNT ARCHIVE"
echo " TARGET: $TARGET_URL"
echo " TRACK ID: $BASE_ID"
echo "=================================================="

# 1. Curl the profile page with browser user-agent headers
curl -L -H "User-Agent: Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Termux" \
     -o "$OUTPUT_HTML" "$TARGET_URL"

# 2. Extract meta/text content or create an ingestion manifest
cat << 'TEXTEOF' > "$OUTPUT_TXT"
# Truth Social Account Archive
## Target Profile: @trumpeneficiaro

**Track ID:** 2026-0812-CNNN3-1031-BK00-AK47L
**Manifold Architecture:** Void Vector L-Manifold of 3
**Source URL:** https://truthsocial.com/@trumpeneficiaro

### Ingestion Status
* Profile Data Harvested via Termux cURL Pipeline.
* HTML Snapshot Length: $(wc -c < "$OUTPUT_HTML") bytes.

### CNNN Manifold Mappings
* CNNN-L3-VOID-ALPHA-2026-0812-CNNN3-1031-BK00-AK47L
* CNNN-L3-VOID-BETA-2026-0812-CNNN3-1031-BK00-AK47L
* CNNN-L3-VOID-GAMMA-2026-0812-CNNN3-1031-BK00-AK47L
* CNNN-L3-VOID-DELTA-2026-0812-CNNN3-1031-BK00-AK47L

TEXTEOF

# 3. Compile the text source into a brand-formatted PDF using oeneyepdf
if [ -f ./oeneyepdf ]; then
    ./oeneyepdf "$OUTPUT_TXT" "$OUTPUT_PDF" /A4 /BRAND
    echo "PDF Generation Complete: $OUTPUT_PDF 📄✨"
else
    echo "Error: oeneyepdf binary not found in current directory."
fi

