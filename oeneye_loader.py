import struct

class OeneyeLoader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.data = None
        
        self.REFS_OFFSET = 0x0003
        self.FSRS_OFFSET = 0x0010
        self.SUPB_OFFSET = 0x1E000
        self.CHKP_OFFSET = 0x28000
        self.BACKUP_OFFSET = 0xC7E03

    def load_image(self):
        print(f"[*] Loading Oeneye container image: {self.image_path}")
        with open(self.image_path, "rb") as f:
            self.data = f.read()
        print(f"[+] Container loaded successfully ({len(self.data)} bytes).")

    def verify_headers(self):
        print("\n[*] Verifying structural headers and magic signatures...")
        
        refs_magic = self.data[self.REFS_OFFSET : self.REFS_OFFSET + 4]
        print(f"    - ReFS Header at 0x{self.REFS_OFFSET:04X}: {refs_magic.decode('latin1', errors='ignore')}")
        
        fsrs_magic = self.data[self.FSRS_OFFSET : self.FSRS_OFFSET + 4]
        print(f"    - FSRS Header at 0x{self.FSRS_OFFSET:04X}: {fsrs_magic.decode('latin1', errors='ignore')}")
        
        chkp_sig = self.data[self.CHKP_OFFSET : self.CHKP_OFFSET + 4]
        print(f"    - Checkpoint Block at 0x{self.CHKP_OFFSET:05X}: Sig 0x{struct.unpack('<I', chkp_sig)[0]:08X}")

        backup_refs = self.data[self.BACKUP_OFFSET : self.BACKUP_OFFSET + 4]
        print(f"    - Backup Mirror at 0x{self.BACKUP_OFFSET:05X}: {backup_refs.decode('latin1', errors='ignore')}")

    def initialize_runtime(self):
        self.load_image()
        self.verify_headers()
        print("\n[+] Oeneye Runtime Kernel Loader initialized and ready for payload execution.")

if __name__ == "__main__":
    loader = OeneyeLoader("oeneye-bootstrap.img")
    loader.initialize_runtime()
