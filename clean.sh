#!/usr/bin/env bash
set -euo pipefail

echo "Cleaning up auxiliary LaTeX files..."
rm -f *.aux *.log *.bbl *.blg *.toc *.out
echo "Cleanup complete."
