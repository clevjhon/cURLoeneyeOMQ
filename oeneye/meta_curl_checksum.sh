#!/data/data/com.termux/files/usr/bin/bash
set -e

# Meta AI endpoints
META_URL="https://www.meta.ai/"
MUSE_SPARK_URL="https://www.meta.ai/muse-spark"

echo "==> 1. Meta AI curl..."
curl -sSL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -w "\nHTTP Status: %{http_code}\n" \
  -o meta_response.html \
  "$META_URL"

echo "==> 2. Calculating SHA-256..."
sha256sum meta_response.html | tee meta_response.html.sha256
echo "69fb43138b6e53bf31a86477558e32eb9dabfb7fbe4db9c41bfcdfc3b2755d46  oeneye_this_chat.log" | tee -a meta_combined.sha256
cat meta_response.html.sha256 >> meta_combined.sha256
cat combined_checksums.sha256 >> meta_combined.sha256

echo "==> 3. Verify all..."
sha256sum -c meta_combined.sha256
sha256sum -c combined_checksums.sha256

echo "==> 4. Envelope verify_4096()..."
cargo run
