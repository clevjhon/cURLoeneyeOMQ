import struct
from chaosnet_codec import OPCODES
from bridge_oeneye_chaosnet import wrap_oeneye_packet

class OeneyeNetworkSimulator:
    def __init__(self, image_path):
        self.image_path = image_path
        self.rom_data = None
        self.virtual_memory = bytearray(0x100000)
        self.segments = {
            "ROOT_REFS": 0x0003,
            "SUPB": 0x1E000,
            "CHKP": 0x28000,
        }
        self.network_outbox = []

    def load_and_boot(self):
        print(f"[*] Loading ROM image: {self.image_path}")
        with open(self.image_path, "rb") as f:
            self.rom_data = f.read()
        
        print("[*] Mapping segments into virtual runtime memory...")
        for name, offset in self.segments.items():
            block_data = self.rom_data[offset : offset + 32]  # Grab 32-byte chunk
            self.virtual_memory[offset : offset + len(block_data)] = block_data
            print(f"    - Mapped [{name}] at 0x{offset:05X}")

    def broadcast_segments(self):
        print("\n========================================")
        print("   OENEYE KERNEL NETWORK BROADCAST")
        print("========================================")
        
        for name, offset in self.segments.items():
            # Extract segment payload from virtual memory
            payload = bytes(self.virtual_memory[offset : offset + 32])
            
            # Encapsulate into a Chaosnet frame (Opcode 1: RFC)
            frame = wrap_oeneye_packet(payload, opcode=1, src_addr=0o100, dest_addr=0o200)
            self.network_outbox.append((name, frame))
            
            print(f"[bcast] Segment '{name}' broadcasted ({len(frame)} bytes total frame).")
        
        print(f"\n[+] Outbox contains {len(self.network_outbox)} ready-to-transmit frames.")
        print("========================================")

if __name__ == "__main__":
    sim = OeneyeNetworkSimulator("oeneye-bootstrap.img")
    sim.load_and_boot()
    sim.broadcast_segments()
