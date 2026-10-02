from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3

class OAIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "verb=ListRecords" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            
            conn = sqlite3.connect('invoice_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, channel, entity FROM invoices;")
            rows = cursor.fetchall()
            conn.close()

            xml_payload = '<?xml version="1.0" encoding="UTF-8"?>\n<OAI-PMH>\n'
            for r in rows:
                xml_payload += f"  <record>\n    <header><identifier>oeneye:invoice:{r[0]}</identifier></header>\n"
                xml_payload += f"    <metadata><channel>{r[1]}</channel><entity>{r[2]}</entity></metadata>\n  </record>\n"
            xml_payload += '</OAI-PMH>'
            
            self.wfile.write(xml_payload.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), OAIHandler)
    print("OAI-PMH Provider running on port 8080...")
    server.serve_forever()
