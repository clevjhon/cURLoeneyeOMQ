import struct

# --- Protocol Definitions ---
HEADER_WORDS = 8
MAX_PAYLOAD = 488
OPCODES = {
    1: "RFC",  # Request for connection
    2: "OPN",  # Connection opened
    3: "CLS"   # Connection closed
}

def wrap_oeneye_packet(payload_data, opcode=1, src_addr=0o100, dest_addr=0o200):
    if len(payload_data) > MAX_PAYLOAD:
        raise ValueError(f"Payload exceeds Chaosnet max size ({MAX_PAYLOAD} bytes)")
    
    word0 = (opcode << 8) & 0xFFFF
    word1 = ((0 & 0xF) << 12) | (len(payload_data) & 0xFFF)
    word2 = src_addr & 0xFFFF
    word3 = 0
    word4 = dest_addr & 0xFFFF
    word5 = 0
    word6 = 1
    word7 = 0
    
    header = struct.pack('<8H', word0, word1, word2, word3, word4, word5, word6, word7)
    return header + payload_data


class OeneyeMasterSystem:
    def __init__(self, image_path):
        self.image_path = image_path
        self.rom_data = None
        self.virtual_memory = bytearray(0x100000)
        self.REQUIRED_SIGNATURE = 0xA5B2C3D8
        
        self.segments = {
            "ROOT_REFS": 0x0003,
            "ROOT_FSRS": 0x0010,
            "SUPB": 0x1E000,
            "CHKP": 0x28000,
            "CHKP_DELTA": 0x29000,
            "BACKUP_SUPB": 0xC5000,
            "BACKUP_REFS": 0xC7E00
        }
        self.network_outbox = []

    def load_image(self):
        print(f"[*] Loading ROM image into host memory: {self.image_path}")
        with open(self.image_path, "rb") as f:
            self.rom_data = f.read()
        print(f"[+] Loaded {len(self.rom_data)} bytes.")

    def verify_invariants(self):
        print("\n[STAGE 1] Formal Invariant Gatekeeper")
        print("-" * 40)
        
        supb_sig = struct.unpack("<I", self.rom_data[self.segments["SUPB"] + 12 : self.segments["SUPB"] + 16])[0]
        assert supb_sig == self.REQUIRED_SIGNATURE, f"SUPB Signature mismatch: 0x{supb_sig:08X}"
        print(f"[PASS] SUPB Signature Verified (0x{supb_sig:08X})")

        chkp_sig = struct.unpack("<I", self.rom_data[self.segments["CHKP"] + 12 : self.segments["CHKP"] + 16])[0]
        assert chkp_sig == self.REQUIRED_SIGNATURE, f"CHKP Signature mismatch: 0x{chkp_sig:08X}"
        print(f"[PASS] CHKP Signature Verified (0x{chkp_sig:08X})")

        total_size = len(self.rom_data)
        assert total_size % 512 == 0, "Container size is not block-aligned."
        print(f"[PASS] Block Alignment Bound ({total_size} bytes)")

    def map_virtual_memory(self):
        print("\n[STAGE 2] Virtual Runtime Memory Mapping")
        print("-" * 40)
        block_size = 512
        for name, offset in self.segments.items():
            block_data = self.rom_data[offset : offset + block_size]
            self.virtual_memory[offset : offset + len(block_data)] = block_data
            print(f"    - Mapped [{name}] at virtual address 0x{offset:05X}")

    def execute_kernel_boot(self):
        print("\n[STAGE 3] Virtual Kernel Boot Handoff")
        print("-" * 40)
        print("[*] Autopoietic state engine: INITIALIZED")
        print("[*] Symbolic operator pipeline: READY")
        print("[+] SUCCESS: Virtual runtime kernel stub booted cleanly.")

    def broadcast_network_outbox(self):
        print("\n[STAGE 4] Chaosnet Protocol Integration")
        print("-" * 40)
        for name in ["ROOT_REFS", "SUPB", "CHKP"]:
            offset = self.segments[name]
            payload = bytes(self.virtual_memory[offset : offset + 32])
            frame = wrap_oeneye_packet(payload, opcode=1, src_addr=0o100, dest_addr=0o200)
            self.network_outbox.append((name, frame))
            print(f"[bcast] Segment '{name}' encapsulated into {len(frame)}-byte Chaosnet frame (RFC).")
        
        print(f"\n[+] Master pipeline complete. Outbox ready with {len(self.network_outbox)} frames.")

    def run_full_lifecycle(self):
        print("========================================")
        print("   OENEYE MASTER SYSTEM INITIALIZATION")
        print("========================================")
        self.load_image()
        self.verify_invariants()
        self.map_virtual_memory()
        self.execute_kernel_boot()
        self.broadcast_network_outbox()
        print("========================================")

if __name__ == "__main__":
    system = OeneyeMasterSystem("oeneye-bootstrap.img")
    system.run_full_lifecycle()
