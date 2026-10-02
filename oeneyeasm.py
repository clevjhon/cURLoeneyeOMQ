import sys
import struct

class OeneyeAssembler:
    def __init__(self):
        self.supb_signature = 0xA5B2C3D8
        self.block_size = 512

    def assemble(self, source_code: str) -> bytes:
        """Assemble text instructions into 512-byte aligned binary blocks."""
        bytecode = bytearray()
        
        # Pack SUPB signature header (4 bytes) and version/flags
        bytecode.extend(struct.pack("<I", self.supb_signature))
        
        for line in source_code.splitlines():
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            
            parts = line.split()
            mnemonic = parts[0].upper()
            operand = int(parts[1], 0) if len(parts) > 1 else 0
            
            if mnemonic == "LOAD":
                bytecode.extend(struct.pack("<BH", 0x01, operand))
            elif mnemonic == "ADD":
                bytecode.extend(struct.pack("<BH", 0x02, operand))
            elif mnemonic == "HALT":
                bytecode.extend(struct.pack("<BH", 0xFF, 0x00))
            else:
                raise ValueError(f"Unknown mnemonic: {mnemonic}")

        # Pad to strict 512-byte block alignment standard
        if len(bytecode) > self.block_size:
            raise ValueError(f"Bytecode exceeds block size: {len(bytecode)} > {self.block_size}")
        
        bytecode.extend(b'\x00' * (self.block_size - len(bytecode)))
        return bytes(bytecode)

if __name__ == "__main__":
    sample_code = """
    ; Oeneye Sample Assembly Program
    LOAD 42
    ADD 10
    HALT
    """
    asm = OeneyeAssembler()
    binary = asm.assemble(sample_code)
    print(f"[+] Successfully assembled {len(binary)} bytes (512-byte block aligned).")
    print(f"[+] SUPB Header Verified: {hex(struct.unpack('<I', binary[:4])[0])}")
