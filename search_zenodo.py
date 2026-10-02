import json
import urllib.parse
import urllib.request

query = 'metadata.creators.person_or_org.name:"Ketelhut, Kai Olaf"'
encoded_query = urllib.parse.quote(query)
url = f"https://zenodo.org/api/records?q={encoded_query}&size=10"

print(f"Querying Zenodo API for: {query}")
req = urllib.request.Request(
    url, 
    headers={"Accept": "application/json", "User-Agent": "TermuxScript/1.0"}
)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
except Exception as e:
    print(f"Error querying Zenodo API: {e}")
    exit(1)

hits = data.get('hits', {}).get('hits', [])
print(f"Found {len(hits)} matching record(s).\n")

for idx, record in enumerate(hits, 1):
    rec_id = record.get('id')
    metadata = record.get('metadata', {})
    title = metadata.get('title', 'No Title')
    files = record.get('files', [])
    
    print(f"[{idx}] Record ID: {rec_id}")
    print(f"    Title: {title}")
    print(f"    Files attached: {len(files)}")
    
    for file_item in files:
        file_key = file_item.get('key')
        file_url = file_item.get('links', {}).get('self')
        if not file_url:
            file_url = f"https://zenodo.org/api/records/{rec_id}/files/{file_key}/content"
            
        print(f"    -> Downloading file: {file_key}")
        try:
            file_req = urllib.request.Request(file_url, headers={"User-Agent": "TermuxScript/1.0"})
            with urllib.request.urlopen(file_req) as f_res, open(file_key, 'wb') as out_f:
                out_f.write(f_res.read())
            print(f"       Successfully saved: {file_key}")
        except Exception as fe:
            print(f"       Error downloading {file_key}: {fe}")
    print("-" * 40)

print("Search execution and downloads complete!")
