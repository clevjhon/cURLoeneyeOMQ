import json
import urllib.request

with open('record.json', 'r') as f:
    data = json.load(f)

files = data.get('files', [])
print(f"Found {len(files)} files to download.")

for item in files:
    key = item['key']
    url = item['links']['self']
    print(f"Downloading -> {key}")
    try:
        urllib.request.urlretrieve(url, key)
        print(f"Successfully saved: {key}")
    except Exception as e:
        print(f"Error downloading {key}: {e}")

print("All downloads complete!")
