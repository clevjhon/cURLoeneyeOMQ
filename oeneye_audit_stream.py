import struct
import hashlib
from datetime import datetime
from oeneye_master_init import OeneyeMasterSystem, wrap_oeneye_packet
from decode_oeneye_chaosnet import unwrap_oeneye_packet

class AuditLogger:
    def __init__(self, log_path="oeneye_audit.log"):
        self.log_path = log_path

    def log_event(self, event_type, details):
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] [{event_type}] {details}\n"
        with open(self.log_path, "a") as f:
            f.write(log_entry)
        print(f"[AUDIT] {details}")

class OeneyeStreamer:
    def __init__(self, system, logger):
        self.system = system
        self.logger = logger

    def stream_segment(self, name, offset, chunk_size=32):
        self.logger.log_event("STREAM_START", f"Initiating chunked stream for segment '{name}' at 0x{offset:05X}")
        
        block_data = self.system.virtual_memory[offset : offset + 512]
        packet_num = 1
        
        for i in range(0, len(block_data), chunk_size):
            chunk = block_data[i : i + chunk_size]
            if not chunk or all(b == 0 for b in chunk):
                break  # Skip empty padding blocks
                
            payload_hash = hashlib.sha256(chunk).hexdigest()[:12]
            
            # Wrap into Chaosnet frame (Opcode 1: RFC / Data Stream)
            frame = wrap_oeneye_packet(chunk, opcode=1, src_addr=0o100, dest_addr=0o200)
            decoded = unwrap_oeneye_packet(frame)
            
            detail_str = (
                f"Segment: {name} | Chunk {packet_num} | "
                f"Offset: 0x{(offset + i):05X} | "
                f"Bytes: {len(chunk)} | SHA256: {payload_hash} | "
                f"Opcode: {decoded['opcode_name']}"
            )
            self.logger.log_event("PACKET_TX", detail_str)
            packet_num += 1

if __name__ == "__main__":
    print("========================================")
    print("   OENEYE AUDIT STREAM & LOGGER")
    print("========================================")
    
    logger = AuditLogger()
    logger.log_event("SYSTEM_INIT", "Starting Oeneye audit logging and stream session.")

    # Initialize Master System
    system = OeneyeMasterSystem("oeneye-bootstrap.img")
    system.load_image()
    system.verify_invariants()
    system.map_virtual_memory()

    streamer = OeneyeStreamer(system, logger)

    print("\n[Streaming Active Segments]")
    print("-" * 40)
    for name, offset in system.segments.items():
        streamer.stream_segment(name, offset, chunk_size=32)

    logger.log_event("SYSTEM_COMPLETE", "All active segments successfully streamed and audited.")
    print("\n[+] Audit stream complete. Log saved to 'oeneye_audit.log'.")
    print("========================================")
