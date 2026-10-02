import struct
import os

def get_fat_value(fat_data, cluster):
    fat_offset = cluster + (cluster // 2)
    if fat_offset + 1 >= len(fat_data):
        return 0xFFF
    val = struct.unpack("<H", fat_data[fat_offset:fat_offset+2])[0]
    if cluster & 1:
        val >>= 4
    else:
        val &= 0xFFF
    return val

def extract_all_files():
    image_path = "mosfetq-dos.img"
    if not os.path.exists(image_path):
        print(f"[-] Image not found: {image_path}")
        return []

    extracted_assets = []

    with open(image_path, "rb") as f:
        # Read BPB
        f.seek(11)
        bytes_per_sec = struct.unpack("<H", f.read(2))[0]
        sec_per_clus = f.read(1)[0]
        reserved_sec = struct.unpack("<H", f.read(2))[0]
        num_fats = f.read(1)[0]
        root_entries = struct.unpack("<H", f.read(2))[0]
        f.seek(22)
        sec_per_fat = struct.unpack("<H", f.read(2))[0]

        fat_offset = reserved_sec * bytes_per_sec
        fat_size = sec_per_fat * bytes_per_sec
        
        root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
        root_dir_offset = root_dir_sector * bytes_per_sec
        root_dir_sectors = (root_entries * 32 + bytes_per_sec - 1) // bytes_per_sec
        first_data_sector = root_dir_sector + root_dir_sectors

        f.seek(fat_offset)
        fat_data = f.read(fat_size)

        f.seek(root_dir_offset)
        root_dir_data = f.read(root_entries * 32)

        cluster_bytes = sec_per_clus * bytes_per_sec

        for i in range(0, len(root_dir_data), 32):
            entry = root_dir_data[i:i+32]
            if entry[0] == 0x00:
                break
            if entry[0] == 0xE5 or (entry[11] & 0x08): # Skip deleted or volume label
                continue
            
            raw_name = entry[0:11]
            name = raw_name[0:8].decode('ascii', errors='ignore').strip()
            ext = raw_name[8:11].decode('ascii', errors='ignore').strip()
            filename = f"{name}.{ext}" if ext else name
            
            attr = entry[11]
            start_cluster = struct.unpack("<H", entry[26:28])[0]
            file_size = struct.unpack("<I", entry[28:32])[0]

            if attr & 0x10: # Directory
                extracted_assets.append({"name": filename, "type": "DIR", "size": 0, "content": "[Directory Node]"})
                continue

            # Extract file chain
            file_data = bytearray()
            curr_cluster = start_cluster
            while curr_cluster >= 2 and curr_cluster < 0xFF8:
                sector = first_data_sector + (curr_cluster - 2) * sec_per_clus
                f.seek(sector * bytes_per_sec)
                file_data.extend(f.read(cluster_bytes))
                curr_cluster = get_fat_value(fat_data, curr_cluster)
            
            file_data = file_data[:file_size]
            try:
                content_str = file_data.decode('utf-8', errors='replace')
            except:
                content_str = f"[Binary Blob - {file_size} bytes]"

            extracted_assets.append({
                "name": filename,
                "type": "FILE",
                "size": file_size,
                "cluster": start_cluster,
                "content": content_str[:400] + ("..." if file_size > 400 else "")
            })

    return extracted_assets

def generate_html(assets):
    asset_cards = ""
    for asset in assets:
        asset_cards += f"""
        <div class="asset-card">
            <h3>{asset['name']} <span class="badge">{asset['type']}</span></h3>
            <div class="meta">Cluster: {asset.get('cluster', 'N/A')} | Size: {asset['size']} bytes</div>
            <pre>{asset['content']}</pre>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OENEYE Ecosystem - Complete Volume Stream Dashboard</title>
    <style>
        body {{ margin: 0; background: #0b0f0c; color: #00ff66; font-family: 'Courier New', Courier, monospace; padding: 20px; }}
        h1 {{ border-bottom: 2px solid #00ff66; padding-bottom: 10px; color: #fff; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-top: 20px; }}
        .asset-card {{ border: 1px solid #00ff66; background: #050806; padding: 15px; box-shadow: 0 0 10px rgba(0,255,102,0.1); }}
        .badge {{ background: #00ff66; color: #050806; padding: 2px 6px; font-size: 9pt; float: right; font-weight: bold; }}
        .meta {{ font-size: 9pt; color: #88ffbb; margin-bottom: 10px; }}
        pre {{ background: #020403; border: 1px solid #004411; padding: 10px; max-height: 200px; overflow-y: auto; white-space: pre-wrap; font-size: 10pt; }}
    </style>
</head>
<body>
    <h1>OENEYE DOS Ecosystem - Directory Stream Index</h1>
    <p>Automated forensic extraction report for <strong>mosfetq-dos.img</strong> virtual volume assets.</p>
    <div class="grid">
        {asset_cards}
    </div>
</body>
</html>
"""
    with open("oeneye_ecosystem_stream.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("[+] Successfully generated complete dashboard: oeneye_ecosystem_stream.html")

if __name__ == "__main__":
    assets = extract_all_files()
    generate_html(assets)
