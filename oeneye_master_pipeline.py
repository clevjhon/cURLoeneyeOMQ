import sqlite3
import json
import os

print("[*] Initializing Oeneye Master Pipeline...")

# 1. Database Setup & Dual-Channel Ledger Management
conn = sqlite3.connect('invoice_database.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS invoices (id INTEGER PRIMARY KEY AUTOINCREMENT, item_description TEXT, net_amount_eur REAL, vat_amount_eur REAL, total_amount_eur REAL, payment_gateway TEXT);")

try:
    cursor.execute("ALTER TABLE invoices ADD COLUMN channel TEXT DEFAULT 'RETAIL';")
    cursor.execute("ALTER TABLE invoices ADD COLUMN entity TEXT DEFAULT 'Fieldberry Group';")
    cursor.execute("ALTER TABLE invoices ADD COLUMN n_cage TEXT DEFAULT NULL;")
except sqlite3.OperationalError:
    pass

# Ensure at least one baseline record exists
cursor.execute("SELECT COUNT(*) FROM invoices;")
if cursor.fetchone()[0] == 0:
    cursor.execute("""
        INSERT INTO invoices (item_description, net_amount_eur, vat_amount_eur, total_amount_eur, payment_gateway, channel, entity, n_cage)
        VALUES ('Reference Publication (ISBN: 978-3-00-068463-0)', 21.0, 1.47, 22.47, 'https://bunq.me/fieldberry', 'WHOLESALE_INSTITUTIONAL', 'SIETEHR FOUNDATION', 'CNNN3');
    """)
else:
    cursor.execute("""
        UPDATE invoices 
        SET channel = 'WHOLESALE_INSTITUTIONAL',
            entity = 'SIETEHR FOUNDATION',
            n_cage = 'CNNN3'
        WHERE id = 1;
    """)

conn.commit()

# 2. Telemetry Sub-Table Integration (Zenodo Record 21679833)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS telemetry_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zenodo_id TEXT,
        system_identifier TEXT,
        location TEXT,
        protocol TEXT,
        json_payload TEXT
    );
''')

mainframe_data = {
    "identifier": "QUANTUMTHERMOSTATIC-CORE-01",
    "location": "Berlin, Germany",
    "operational_sprint": "3-Month Clinical & Technical Roadmap",
    "ftp_account": "qt_mainframe_ftp",
    "access_level": "Secure Restricted (Bank-Grade Encryption Compliant)",
    "protocol": "SFTP/FTPS over Calibrated Inertial Thresholds",
    "authentication_mode": "Public Key Infrastructure (PKI) + Zero-Trust Runtime Verification"
}

# Check if telemetry record already exists to avoid duplication
cursor.execute("SELECT COUNT(*) FROM telemetry_records WHERE zenodo_id = '21679833';")
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO telemetry_records (zenodo_id, system_identifier, location, protocol, json_payload)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        "21679833",
        mainframe_data["identifier"],
        mainframe_data["location"],
        mainframe_data["protocol"],
        json.dumps(mainframe_data, indent=2)
    ))
    conn.commit()

conn.close()
print("[+] Database records and telemetry synchronized.")

# 3. Virtual Filesystem Index Synchronization (emu_dos.py target)
index_file = 'dos_filesystem_index.json'
fs_index = {
    "virtual_drive": "C:\\OENEYE",
    "system_identifier": "QUANTUMTHERMOSTATIC-CORE-01",
    "files": [
        {
            "filename": "MAINFRAME.DAT",
            "zenodo_id": "21679833",
            "path": "C:\\OENEYE\\TELEMETRY\\MAINFRAME.DAT",
            "description": "Obsidian Brain Mainframe Declaration parameters"
        }
    ]
}

with open(index_file, 'w') as f:
    json.dump(fs_index, f, indent=2)

print(f"[+] Filesystem index bound successfully to {index_file}.")
print("[+] Pipeline complete. Ready for runtime kernel integration.")
