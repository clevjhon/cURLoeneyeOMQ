#!/data/data/com.termux/files/usr/bin/bash
set -e
TARGET_URL="https://claude.ai/share/964a5cf8-d468-4075-9fcc-33b4c4e935f5"

echo "==> Downloading via curl..."
curl -sSL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -w "\nHTTP Status: %{http_code}\n" \
  -o ximg_response.html \
  "$TARGET_URL"

echo "==> Calculating SHA-256 checksum..."
sha256sum ximg_response.html | tee ximg_response.html.sha256

echo "==> Checksum generation complete under ns_HOLLA."
echo "==> Running envelope.verify_4096()..."
cargo run
