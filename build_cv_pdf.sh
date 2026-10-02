#!/data/data/com.termux/files/usr/bin/bash

# 1. Create source text file formatted with oeneyePDF markdown specs
cat << 'TEXTEOF' > cv_source.txt
# Rheinmetall India Enterprise CV
## Enterprise Systems & Architecture Node

**Track ID:** 2026-0812-CNNN3-1031-BK00-AK47
**Entity:** Kai Ketelhut (Dipl.-Ing. / Patent Engineer)
**Operations:** Berlin / India

### ERP Ledger Nodes
* CNNN3-oeneyeSAP-ERP-FI
* CNNN3-oeneyeSAP-ERP-CO
* CNNN3-oeneyeSAP-ERP-MM
* CNNN3-oeneyeSAP-ERP-SD
* CNNN3-oeneyeSAP-ERP-PP

### CV / Card Entity Nodes
* Rheinmetall-India-Enterprise-Systems-PROFILE
* Rheinmetall-India-Enterprise-Systems-CREDENTIALS
* Rheinmetall-India-Enterprise-Systems-COMPLIANCE
* Rheinmetall-India-Enterprise-Systems-LEDGERS
* Rheinmetall-India-Enterprise-Systems-DEPLOYMENT

TEXTEOF

# 2. Compile oeneyepdf.c if not already built
if [ ! -f ./oeneyepdf ]; then
    gcc oeneyepdf.c -o oeneyepdf
fi

# 3. Generate the PDF
./oeneyepdf cv_source.txt rheinmetall_cv.pdf /A4 /BRAND

echo "PDF Generation Complete: rheinmetall_cv.pdf 📄✨"
