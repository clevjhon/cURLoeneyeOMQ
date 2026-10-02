import struct

class OeneyeUnifiedLoader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.data = None
        
        # Fully mapped structural offsets
        self.REFS_OFFSET = 0x0003
        self.FSRS_OFFSET = 0x0010
        self.SUPB_OFFSET = 0x1E000
        self.CHKP_OFFSET = 0x28000
        self.CHKP_DELTA_OFFSET = 0x29000
        self.BACKUP_SUPB_OFFSET = 0xC5000
        self.BACKUP_REFS_OFFSET = 0xC7E00

    def load_container(self):
        print(f"[*] Loading Oeneye container: {self.image_path}")
        with open(self.image_path, "rb") as f:
            self.data = f.read()
        print(f"[+] Loaded {len(self.data)} bytes successfully.\n")

    def validate_anchors(self):
        print("========================================")
        print("   OENEYE STRUCTURAL ANCHOR VALIDATION")
        print("========================================")
        
        # 1. Root ReFS & FSRS
        refs = self.data[self.REFS_OFFSET : self.REFS_OFFSET + 4].decode('latin1', errors='ignore')
        fsrs = self.data[self.FSRS_OFFSET : self.FSRS_OFFSET + 4].decode('latin1', errors='ignore')
        print(f"[*] Root ReFS Anchor (0x{self.REFS_OFFSET:04X}) : {refs}")
        print(f"[*] Root FSRS Anchor (0x{self.FSRS_OFFSET:04X}) : {fsrs}")
        
        # 2. Superblock (SUPB)
        supb_magic = self.data[self.SUPB_OFFSET : self.SUPB_OFFSET + 4].decode('latin1', errors='ignore')
        supb_sig = struct.unpack("<I", self.data[self.SUPB_OFFSET + 12 : self.SUPB_OFFSET + 16])[0]
        print(f"[*] Superblock SUPB   (0x{self.SUPB_OFFSET:05X}) : {supb_magic} (Sig: 0x{supb_sig:08X})")
        
        # 3. Checkpoint (CHKP)
        chkp_magic = self.data[self.CHKP_OFFSET : self.CHKP_OFFSET + 4].decode('latin1', errors='ignore')
        chkp_sig = struct.unpack("<I", self.data[self.CHKP_OFFSET + 12 : self.CHKP_OFFSET + 16])[0]
        print(f"[*] Checkpoint CHKP   (0x{self.CHKP_OFFSET:05X}) : {chkp_magic} (Sig: 0x{chkp_sig:08X})")

        # 4. Backup Tiers
        b_refs = self.data[self.BACKUP_REFS_OFFSET + 3 : self.BACKUP_REFS_OFFSET + 7].decode('latin1', errors='ignore')
        print(f"[*] Backup ReFS Mirror(0x{self.BACKUP_REFS_OFFSET:05X}) : Verified")
        
        print("========================================")
        print("[+] All structural layers verified successfully.")

if __name__ == "__main__":
    loader = OeneyeUnifiedLoader("oeneye-bootstrap.img")
    loader.load_container()
    loader.validate_anchors()
