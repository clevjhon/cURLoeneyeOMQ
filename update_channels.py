import sqlite3
import json

# Connect to database
conn = sqlite3.connect('invoice_database.db')
cursor = conn.cursor()

# 1. Alter table to support channel differentiation if not already present
try:
    cursor.execute("ALTER TABLE invoices ADD COLUMN channel TEXT DEFAULT 'RETAIL';")
    cursor.execute("ALTER TABLE invoices ADD COLUMN entity TEXT DEFAULT 'Fieldberry Group';")
    cursor.execute("ALTER TABLE invoices ADD COLUMN n_cage TEXT DEFAULT NULL;")
    conn.commit()
    print("[+] Database schema updated with channel columns.")
except sqlite3.OperationalError:
    print("[*] Columns already exist, skipping alteration.")

# 2. Insert or update records to reflect Wholesale / Institutional channel
# Based on SIETEHR FOUNDATION fulfillment profile (NCAGE: CNNN3)[span_0](start_span)[span_0](end_span)
cursor.execute("""
    UPDATE invoices 
    SET channel = 'WHOLESALE_INSTITUTIONAL',
        entity = 'SIETEHR FOUNDATION',
        n_cage = 'CNNN3'
    WHERE id = 1;
""")
conn.commit()

# 3. Fetch and generate dual-channel JSON output
cursor.execute('SELECT * FROM invoices;')
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

output_records = []
for row in rows:
    row_dict = dict(zip(columns, row))
    record_id = row_dict.get('id', 1)
    channel = row_dict.get('channel', 'RETAIL')
    
    # Assign specific codex prefixes based on channel type
    if channel == 'WHOLESALE_INSTITUTIONAL':
        codex_id = f"2026-0812-CNNN3-BK01-{record_id:02d}"
        gateway = "https://bunq.me/fieldberry"
    else:
        codex_id = f"2026-RETAIL-BK01-{record_id:02d}"
        gateway = row_dict.get('payment_gateway', 'bunq.me/')

    payload = {
        "oeneye_codex_id": codex_id,
        "distribution_channel": channel,
        "fulfillment_entity": row_dict.get('entity'),
        "ncage_code": row_dict.get('n_cage'),
        "payment_gateway": gateway,
        "invoice_record": row_dict
    }
    output_records.append(payload)

# Save dual-channel JSON output
filename = 'oeneye_dual_channel_ledger.json'
with open(filename, 'w') as f:
    json.dump(output_records, f, indent=2)

print(f"[+] Dual-channel ledger generated: {filename}")
conn.close()
