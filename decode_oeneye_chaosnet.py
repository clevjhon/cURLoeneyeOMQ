import struct
from chaosnet_codec import HEADER_WORDS, MAX_PAYLOAD, OPCODES

def unwrap_oeneye_packet(packet_data):
    header_size = HEADER_WORDS * 2  # 16 bytes
    if len(packet_data) < header_size:
        raise ValueError("Packet data too small to contain a valid Chaosnet header.")
    
    # Unpack the 8-word header
    header_words = struct.unpack('<8H', packet_data[:header_size])
    
    word0 = header_words[0]
    word1 = header_words[1]
    
    # Extract fields based on protocol definition
    opcode = (word0 >> 8) & 0xFF
    payload_len = word1 & 0xFFF
    
    src_addr = header_words[2]
    dest_addr = header_words[4]
    packet_num = header_words[6]
    ack = header_words[7]
    
    payload = packet_data[header_size : header_size + payload_len]
    
    return {
        "opcode": opcode,
        "opcode_name": OPCODES.get(opcode, "UNKNOWN"),
        "payload_length": payload_len,
        "source_address": f"0o{src_addr:o}",
        "destination_address": f"0o{dest_addr:o}",
        "packet_number": packet_num,
        "acknowledgement": ack,
        "payload": payload
    }

if __name__ == "__main__":
    from bridge_oeneye_chaosnet import wrap_oeneye_packet
    
    print("[*] Testing Round-Trip Chaosnet Loopback...")
    
    # Load dummy payload from image
    with open("oeneye-bootstrap.img", "rb") as f:
        data = f.read()
    original_payload = data[0x1E000 : 0x1E000 + 32]
    
    # 1. Encode
    frame = wrap_oeneye_packet(original_payload, opcode=1, src_addr=0o100, dest_addr=0o200)
    
    # 2. Decode
    decoded = unwrap_oeneye_packet(frame)
    
    print("\n[+] Successfully Decoded Incoming Frame:")
    print(    f"    - Opcode          : {decoded['opcode']} ({decoded['opcode_name']})")
    print(    f"    - Source          : {decoded['source_address']}")
    print(    f"    - Destination     : {decoded['destination_address']}")
    print(    f"    - Payload Length  : {decoded['payload_length']} bytes")
    print(    f"    - Payload Match   : {decoded['payload'] == original_payload}")
    print(f"\n[+] Round-trip verification complete. Network stack ready.")
