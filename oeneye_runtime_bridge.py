import os
import time
import threading
import http.server
import socketserver

PORT = 8080
LOG_FILE = "oeneye_kernel_runtime.log"

# Initialize a mock kernel activity log if missing
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("[00:00:01] OENEYE-OS Kernel Initialized.\n")
        f.write("[00:00:02] Autopoietic cycle engine active.\n")
        f.write("[00:00:03] FAT12 Virtual Disk Stream Proxy operational.\n")

class OeneyeStreamHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/live-stream":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            
            try:
                with open(LOG_FILE, "r") as f:
                    f.seek(0, os.SEEK_END)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.5)
                            continue
                        self.wfile.write(f"data: {line.strip()}\n\n".encode("utf-8"))
                        self.wfile.flush()
            except Exception:
                pass
        else:
            return super().do_GET()

    def log_message(self, format, *args):
        pass

def simulate_kernel_activity():
    while True:
        time.sleep(3)
        timestamp = time.strftime("%H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [AUTOPOIESIS] Structural epsilon node verified across cluster chain.\n")

if __name__ == "__main__":
    # Start background kernel simulator thread
    sim_thread = threading.Thread(target=simulate_kernel_activity, daemon=True)
    sim_thread.start()

    # Start HTTP server with Server-Sent Events (SSE) support
    server = socketserver.TCPServer(("", PORT), OeneyeStreamHandler)
    print(f"[*] OENEYE Runtime Bridge active on http://localhost:{PORT}")
    print(f"[*] Live log stream endpoint ready at http://localhost:{PORT}/live-stream")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down bridge.")
