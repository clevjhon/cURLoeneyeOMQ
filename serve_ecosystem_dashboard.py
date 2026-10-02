import http.server
import socketserver
import urllib.request
import threading
import time

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server_thread = threading.Thread(target=lambda: socketserver.TCPServer(("", PORT), Handler).serve_forever(), daemon=True)
    server_thread.start()
    time.sleep(0.5)
    print(f"[*] Ecosystem HTTP server running on port {PORT}")

    url = f"http://localhost:{PORT}/oeneye_ecosystem_stream.html"
    try:
        with urllib.request.urlopen(url) as resp:
            print(f"[+] Proxy Verification Status: {resp.status}")
            print(f"[+] Content-Type: {resp.headers.get('Content-Type')}")
            print(f"[+] Dashboard Stream Header Verified Successfully!")
    except Exception as e:
        print(f"[-] Verification Failed: {e}")
