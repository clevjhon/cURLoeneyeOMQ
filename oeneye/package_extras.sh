#!/usr/bin/env bash
set -e
echo "Building components..."
gcc -c optimizer.c -o optimizer.o
python3 -m py_compile db_journal.py
echo "Done."
