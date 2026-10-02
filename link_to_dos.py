import json
import os

# Filesystem index target for emu_dos.py
index_file = 'dos_filesystem_index.json'

if os.path.exists(index_file):
    with open(index_file, 'r') as f:
        fs_index = json.load(f)
else:
    fs_index = {
        "virtual_drive": "C:\\OENEYE",
        "system_identifier": "QUANTUMTHERMOSTATIC-CORE-01",
        "files": []
    }

# Register the Zenodo record 21679833 mainframe declaration[span_0](start_span)[span_0](end_span)
new_entry = {
    "filename": "MAINFRAME.DAT",
    "zenodo_id": "21679833",
    "path": "C:\\OENEYE\\TELEMETRY\\MAINFRAME.DAT",
    "description": "Obsidian Brain Mainframe Declaration parameters"
}

if new_entry not in fs_index["files"]:
    fs_index["files"].append(new_entry)

with open(index_file, 'w') as f:
    json.dump(fs_index, f, indent=2)

print(f"[+] Successfully mapped MAINFRAME.DAT to {index_file}")
