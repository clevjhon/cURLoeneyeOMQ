import json
import urllib.request
import urllib.error

def main():
    token = input("Enter your Zenodo Personal Access Token: ").strip()
    if not token:
        print("Token cannot be empty.")
        return

    base_url = "https://zenodo.org/api/deposit/depositions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Create Deposition
    print("Creating new deposition...")
    req = urllib.request.Request(base_url, data=b"{}", headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            depo_id = data["id"]
            print(f"Successfully created deposition ID: {depo_id}")
    except urllib.error.HTTPError as e:
        print(f"Failed to create deposition: {e.code} - {e.read().decode()}")
        return

    # 2. Update Metadata
    print("Uploading metadata.json...")
    with open("metadata.json", "rb") as f:
        meta_data = f.read()
    
    meta_url = f"{base_url}/{depo_id}"
    req = urllib.request.Request(meta_url, data=meta_data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as response:
            print("Metadata updated successfully.")
    except urllib.error.HTTPError as e:
        print(f"Failed to update metadata: {e.code} - {e.read().decode()}")
        return

    print(f"\n--- SUCCESS ---")
    print(f"Deposition ID {depo_id} is ready.")
    print(f"To upload your PDF, run:")
    print(f'curl -X POST "{base_url}/{depo_id}/files" -H "Authorization: Bearer {token}" -F "file=@monograph.pdf"')

if __name__ == "__main__":
    main()
