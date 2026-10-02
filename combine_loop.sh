#!/data/data/com.termux/files/usr/bin/bash

BASE_ID="2026-0812-CNNN3-1031-BK00-AK47"
PREFIX="CNNN3"
TARGET="oeneye"

# Loop through different system components to combine them
for component in OS SDK DOS KERNEL; do
    COMBINED_NAME="${PREFIX}-${TARGET}-${component}"
    echo "Target: $COMBINED_NAME (Base: $BASE_ID) 💖"
    
    # You can add your build or file handling commands here
    # touch "${COMBINED_NAME}.img"
done

