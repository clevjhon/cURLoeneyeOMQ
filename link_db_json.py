import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect('invoice_database.db')
cursor = conn.cursor()

# 1. Create a telemetry sub-table with JSON payload support
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

# 2. Define the mainframe declaration dataset
mainframe_data = {
    "identifier": "QUANTUMTHERMOSTATIC-CORE-01",
    "location": "Berlin, Germany",
    "operational_sprint": "3-Month Clinical & Technical Roadmap",
    "ftp_account": "qt_mainframe_ftp",
    "access_level": "Secure Restricted (Bank-Grade Encryption Compliant)",
    "protocol": "SFTP/FTPS over Calibrated Inertial Thresholds",
    "authentication_mode": "Public Key Infrastructure (PKI) + Zero-Trust Runtime Verification"
}

# 3. Insert record into the sub-table
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
print("[+] Successfully registered Zenodo record 21679833 into SQLite telemetry sub-table.")

# 4. Verify insertion by querying back
cursor.execute("SELECT zenodo_id, system_identifier, location FROM telemetry_records;")
for row in cursor.fetchall():
    print(f" -> DB Record: Zenodo ID {row[0]} | System: {row[1]} | Location: {row[2]}")

conn.close()
