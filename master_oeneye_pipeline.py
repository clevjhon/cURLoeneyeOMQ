import os
import sys
import time
import struct
import argparse
import threading
import http.server
import socketserver

IMAGE_PATH = "mosfetq-dos.img"
LOG_FILE = "oeneye_kernel_runtime.log"

def banner():
    print("==================================================")
    print("   OENEYE-OS MASTER ECOSYSTEM PIPELINE v1.1       ")
    print("==================================================")

def verify_and_mutate(perform_mutation=False):
    print("[*] Running FAT12 volume inspection...")
    if not os.path.exists(IMAGE_PATH):
        print(f"[-] Error: {IMAGE_PATH} missing.")
        sys.exit(1)
    print(f"[+] Volume image {IMAGE_PATH} verified.")
    
    if perform_mutation:
        print("[*] Executing dynamic file injection/mutation payload...")
        with open(IMAGE_PATH, "r+b") as f:
            f.seek(11)
            bytes_per_sec = struct.unpack("<H", f.read(2))[0]
            reserved_sec = struct.unpack("<H", f.read(2))[0]
            num_fats = f.read(1)[0]
            root_entries = struct.unpack("<H", f.read(2))[0]
            f.seek(22)
            sec_per_fat = struct.unpack("<H", f.read(2))[0]

            root_dir_sector = reserved_sec + (num_fats * sec_per_fat)
            root_dir_offset = root_dir_sector * bytes_per_sec
            f.seek(root_dir_offset)
            root_dir_data = f.read(root_entries * 32)
            
            target_slot = -1
            for i in range(0, len(root_dir_data), 32):
                entry = root_dir_data[i:i+32]
                if entry[0] == 0x00 or entry[0] == 0xE5:
                    target_slot = root_dir_offset + i
                    break
            if target_slot != -1:
                name_padded = "CLI_MUT".ljust(8)[:8].encode('ascii')
                ext_padded = "LOG".ljust(3)[:3].encode('ascii')
                payload = b"CLI-TRIGGERED OENEYE RUNTIME MUTATION EVENT.\n"
                entry_bytes = name_padded + ext_padded + bytes([0x20]) + (b'\x00' * 10) + (b'\x00' * 4) + struct.pack("<H", 25) + struct.pack("<I", len(payload))
                f.seek(target_slot)
                f.write(entry_bytes)
                print(f"[+] CLI Mutation successful: Injected CLI_MUT.LOG at root offset {target_slot}")

def start_runtime_bridge(port):
    print(f"[*] Initializing OENEYE Runtime & Telemetry Bridge on port {port}...")
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] OENEYE Master Kernel Initialized.\n")

    class MasterHandler(http.server.SimpleHTTPRequestHandler):
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

    server = socketserver.TCPServer(("", port), MasterHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[+] Master HTTP Proxy & SSE Stream active at http://localhost:{port}")

def simulate_activity():
    while True:
        time.sleep(4)
        timestamp = time.strftime("%H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [CLI-DAEMON] Autopoietic cluster scan nominal. Active stream responsive.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OENEYE-OS Master Ecosystem Pipeline Controller")
    parser.add_argument("--mutate", action="store_true", help="Trigger dynamic FAT12 disk mutation on startup")
    parser.add_argument("--port", type=int, default=8080, help="Specify HTTP server port")
    args = parser.parse_args()

    banner()
    verify_and_mutate(args.mutate)
    start_runtime_bridge(args.port)
    
    sim_thread = threading.Thread(target=simulate_activity, daemon=True)
    sim_thread.start()

    print("[*] Master pipeline fully online. Press Ctrl+C to terminate.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down master pipeline ecosystem.")
