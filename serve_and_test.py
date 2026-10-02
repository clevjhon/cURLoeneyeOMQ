import http.server
import socketserver
import threading
import urllib.request
import time

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"[*] Local HTTP server started on port {PORT}")
    time.sleep(1)

    url = f"http://localhost:{PORT}/oeneye_movie.html"
    print(f"[*] Testing pipeline request to: {url}")
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            status = response.status
            content_type = response.headers.get("Content-Type")
            body_preview = response.read(150).decode("utf-8")
            
            print(f"[+] Pipeline Test Successful!")
            print(f"    - HTTP Status: {status}")
            print(f"    - Content-Type: {content_type}")
            print(f"    - Body Preview: {body_preview}...")
    except Exception as e:
        print(f"[-] Pipeline Test Failed: {e}")
