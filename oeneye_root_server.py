import http.server
import socketserver

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("", PORT), Handler) as httpd:
    print(f"[+] Oeneye Root Server active at http://localhost:{PORT}")
    print("[+] Press Ctrl+C to halt the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server halted.")
