import argparse
import hashlib
import subprocess
import urllib.request
from pathlib import Path

DEFAULT_URL = "https://careers.peopleclick.com/careerscp/client_mit/external/profile/applicationStatus.html"
DEFAULT_OUTPUT = "mit_application_status.html"
REPO_NAME = "clevjhon/cURLoeneyeOMQ"

def download_file(url, output_filename):
    print(f"[*] Downloading content from: {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response, open(output_filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"[+] Successfully downloaded: {output_filename}")
        return True
    except Exception as e:
        print(f"[!] Download failed: {e}")
        return False

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def verify_and_generate_artifacts(filename):
    file_path = Path(filename)
    checksum_path = Path(f"{filename}.sha256")

    print(f"[*] Checking local artifact: {filename}...")
    if not file_path.is_file():
        print(f"[!] Error: {filename} not found.")
        return False

    current_hash = calculate_sha256(file_path)
    print(f"[+] Computed SHA-256: {current_hash}")

    with open(checksum_path, "w") as f:
        f.write(f"{current_hash}  {filename}\n")
    print(f"[+] Successfully generated checksum file: {checksum_path.name}")

    with open(checksum_path, "r") as f:
        saved_line = f.readline().strip()
        saved_hash = saved_line.split()[0]

    if current_hash == saved_hash:
        print("[V] Integrity Verification Passed: Checksum matches file hash perfectly.")
        return True
    else:
        print("[X] Integrity Verification Failed: Hash mismatch detected!")
        return False

def git_sync_pipeline(filename):
    checksum_filename = f"{filename}.sha256"
    print(f"[*] Initializing Git sync for {REPO_NAME}...")
    try:
        subprocess.run(["git", "add", filename, checksum_filename], check=True)
        commit_message = f"Automated sync: {filename} and SHA-256 verification"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("[*] Pushing updates to GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"], check=True)
        print(f"[V] Successfully synced artifacts to {REPO_NAME}!")
    except subprocess.CalledProcessError as e:
        print(f"[!] Git operation failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URL Download, Integrity & Automated Sync Pipeline")
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help="Target URL to fetch")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Output filename")
    args = parser.parse_args()

    print("--- oeneyeOMQ URL Fetch, Integrity & Sync Pipeline ---")
    if download_file(args.url, args.output):
        if verify_and_generate_artifacts(args.output):
            git_sync_pipeline(args.output)
        else:
            print("[!] Sync aborted due to integrity check failure.")
    else:
        print("[!] Pipeline aborted due to download failure.")
