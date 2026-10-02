import struct

class Fat77FileSystem:
    def __init__(self):
        self.block_size = 512
        self.supb_signature = 0xA5B2C3D8

    def validate_block(self, block_data: bytes) -> bool:
        """Enforce strict 512-byte block alignment for FAT77 storage."""
        if len(block_data) != self.block_size:
            raise ValueError(f"Block size violation: expected {self.block_size} bytes, got {len(block_data)}")
        return True

    def write_block(self, block_data: bytes) -> bool:
        """Write block data under FAT77 standards."""
        return self.validate_block(block_data)

    def read_fat12_compatibility_block(self, image_data: bytes, block_index: int) -> bytes:
        """
        Read a legacy FAT12 image block, wrapping/padding it to 
        the 512-byte FAT77 standard aligned with the SUPB signature.
        """
        offset = block_index * self.block_size
        if offset >= len(image_data):
            raise IndexError(f"FAT12 image offset {offset} exceeds image size {len(image_data)}")
        
        chunk = image_data[offset:offset + self.block_size]
        
        # Pad chunk to 512 bytes if it's a trailing sector
        if len(chunk) < self.block_size:
            chunk = chunk + b'\x00' * (self.block_size - len(chunk))
            
        self.validate_block(chunk)
        return chunk

if __name__ == "__main__":
    fs = Fat77FileSystem()
    dummy_legacy_image = b'\xEB\x3C\x90' + b'\x00' * 1023
    block = fs.read_fat12_compatibility_block(dummy_legacy_image, 0)
    print(f"[+] FAT12 Compatibility Reader Verified: Read {len(block)} bytes successfully.")
