import struct
from chaosnet_codec import HEADER_WORDS, MAX_PAYLOAD, OPCODES

def wrap_oeneye_packet(payload_data, opcode=1, src_addr=0o100, dest_addr=0o200):
    if len(payload_data) > MAX_PAYLOAD:
        raise ValueError(f"Payload exceeds Chaosnet max size ({MAX_PAYLOAD} bytes)")
    
    # Header layout (8 words, 16 bits each)
    # Word 0: Opcode (high byte) | unused, always 0 (low byte)
    word0 = (opcode << 8) & 0xFFFF
    # Word 1: Forwarding count (high nibble) | Payload length in bytes (12 bits)
    word1 = ((0 & 0xF) << 12) | (len(payload_data) & 0xFFF)
    
    word2 = src_addr & 0xFFFF     # Source address
    word3 = 0                     # Source index
    word4 = dest_addr & 0xFFFF    # Destination address
    word5 = 0                     # Destination index
    word6 = 1                     # Packet number
    word7 = 0                     # Acknowledgement
    
    header = struct.pack('<8H', word0, word1, word2, word3, word4, word5, word6, word7)
    
    # Combine 16-byte header with payload data
    full_packet = header + payload_data
    return full_packet

if __name__ == "__main__":
    print("[*] Initializing Oeneye to Chaosnet Packet Bridge...")
    with open("oeneye-bootstrap.img", "rb") as f:
        data = f.read()
    
    # Grab our SUPB superblock block as a sample payload segment
    supb_block = data[0x1E000 : 0x1E000 + 32]
    
    # Wrap using Opcode 1 (RFC - Request For Connection)
    packet = wrap_oeneye_packet(supb_block, opcode=1)
    
    print(f"[+] Encapsulated {len(supb_block)} bytes of SUPB payload into Chaosnet frame.")
    print(f"[+] Total Packet Size: {len(packet)} bytes (Header: 16 bytes + Payload)")
    print(f"[+] Raw Header Hex: {packet[:16].hex()}")
    print(f"[+] Protocol State: {OPCODES.get(1, 'UNKNOWN')}")
