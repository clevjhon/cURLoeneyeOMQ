import subprocess
import hashlib
import sys

def get_public_ip():
    try:
        # Run curl -s ifconfig.me
        result = subprocess.run(
            ["curl", "-s", "ifconfig.me"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching IP: {e.stderr}")
        sys.exit(1)

def main():
    print("OENEYE IP & Checksum Utility")
    print("-" * 35)
    
    # Fetch IP
    ip_address = get_public_ip()
    print(f"Public IP : {ip_address}")
    
    # Compute Checksums
    sha256_hash = hashlib.sha256(ip_address.encode('utf-8')).hexdigest()
    md5_hash = hashlib.md5(ip_address.encode('utf-8')).hexdigest()
    
    print(f"SHA-256   : {sha256_hash}")
    print(f"MD5       : {md5_hash}")
    print("-" * 35)

if __name__ == "__main__":
    main()

