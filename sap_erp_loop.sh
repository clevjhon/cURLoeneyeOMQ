#!/data/data/com.termux/files/usr/bin/bash

BASE_ID="2026-0812-CNNN3-1031-BK00-AK47"
PREFIX="CNNN3"
MODULE="oeneyeSAP"
SYSTEM="ERP"

# Loop through different ERP ledger components
for ledger in FI CO MM SD PP; do
    SAP_ERP_TARGET="${PREFIX}-${MODULE}-${SYSTEM}-${ledger}"
    echo "ERP Target: $SAP_ERP_TARGET (Base: $BASE_ID) 💼"
done

