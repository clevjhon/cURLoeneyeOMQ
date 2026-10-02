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

    url = f"http://localhost:{PORT}/oeneye_movie_full.html"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        print(f"[+] Final Pipeline Proxy Status: {resp.status}")
        print(f"[+] Content-Type Header: {resp.headers.get('Content-Type')}")
        print(f"[+] Stream Preview snippet:\n{resp.read(250).decode('utf-8')}")
