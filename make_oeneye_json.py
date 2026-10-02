import sqlite3
import json

# Connect to the SQLite invoice database
conn = sqlite3.connect('invoice_database.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM invoices;')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

output_records = []
for row in rows:
    row_dict = dict(zip(columns, row))
    record_id = row_dict.get('id', 1)
    
    # Apply oeneye codex numbering template
    oeneye_id = f"2026-0812-CNNN3-BK01-{record_id:02d}"
    
    payload = {
        "oeneye_codex_id": oeneye_id,
        "runtime_context": "oeneyeOS-kernel-bridge",
        "invoice_record": row_dict
    }
    output_records.append(payload)

# Save to a structured JSON file
filename = 'oeneye_invoices_codex.json'
with open(filename, 'w') as f:
    json.dump(output_records, f, indent=2)

print(f"[+] Successfully generated codex file: {filename}")
print(json.dumps(output_records, indent=2))

conn.close()
