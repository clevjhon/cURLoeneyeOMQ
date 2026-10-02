import struct

class OeneyeAssembler:
    def __init__(self, output_img="oeneye-compiled.img"):
        self.output_img = output_img
        self.container = bytearray(819200) # 800 KB container
        self.SIGNATURE = 0xA5B2C3D8

    def assemble(self):
        print("========================================")
        print("   OENEYE CUSTOM ASSEMBLER")
        print("========================================")

        # Define a sample structured block at SUPB offset (0x1E000)
        supb_offset = 0x1E000
        
        # Instruction stream / Metadata simulation:
        # Opcode (2 bytes), Flags (2 bytes), Target Address (4 bytes), Signature (4 bytes)
        bytecode = struct.pack('<HHII', 0x0001, 0x00FF, 0x0003, self.SIGNATURE)
        
        # Place into container with 512-byte block alignment
        self.container[supb_offset : supb_offset + len(bytecode)] = bytecode

        with open(self.output_img, "wb") as f:
            f.write(self.container)

        print(f"[+] Assembly successful. Image compiled to '{self.output_img}'")
        print(f"[+] Injected signature 0x{self.SIGNATURE:08X} at offset 0x{supb_offset:05X}")
        print("========================================")

if __name__ == "__main__":
    assembler = OeneyeAssembler()
    assembler.assemble()
