#!/usr/bin/env python3
import hashlib
import socket

class OeneyeSocketTable:
    def __init__(self, bind_address="127.0.0.1", port=8000):
        self.bind_address = bind_address
        self.port = port
        self.registry = {}
        print(f"[*] Initializing oeneyeOS Socket Table at {bind_address}:{port} [o∞o]")

    def register_socket(self, socket_id, endpoint_name):
        self.registry[socket_id] = {
            "endpoint": endpoint_name,
            "status": "BOUND",
            "secure_channel": "sslOENEYE"
        }
        print(f"[+] Registered Socket ID {socket_id} -> {endpoint_name}")

    def generate_ssl_framing(self, payload: bytes) -> bytes:
        # Length-prefixed framing with SHA256 integrity check
        sha = hashlib.sha256(payload).digest()
        length_prefix = len(payload).to_bytes(4, byteorder='big')
        framed_packet = length_prefix + sha + payload
        return framed_packet

if __name__ == "__main__":
    st = OeneyeSocketTable()
    st.register_socket(0x80, "Sector3-Core-Stream")
    st.register_socket(0x81, "FAT77-Cluster-Bus")
    
    test_payload = b"oeneyeOS_sslOENEYE_handshake_payload"
    framed = st.generate_ssl_framing(test_payload)
    print(f"[+] Generated sslOENEYE frame: {len(framed)} bytes [SHA256 secured] [o∞o]")
