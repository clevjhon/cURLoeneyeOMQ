import struct
from oeneye_master_init import OeneyeMasterSystem, wrap_oeneye_packet
from decode_oeneye_chaosnet import unwrap_oeneye_packet

class ChaosnetPeerNode:
    def __init__(self, node_address):
        self.node_address = node_address
        self.connection_states = {}

    def handle_incoming_frame(self, frame_data):
        decoded = unwrap_oeneye_packet(frame_data)
        src = decoded['source_address']
        dest = decoded['destination_address']
        opcode = decoded['opcode']
        opcode_name = decoded['opcode_name']
        
        print(f"[Peer Node 0o{self.node_address:o}] Received frame from {src} -> {dest}")
        print(f"    - Opcode: {opcode} ({opcode_name})")
        print(f"    - Payload Size: {decoded['payload_length']} bytes")

        # State Machine Transition
        if opcode == 1:  # RFC - Request For Connection
            print(f"    -> [STATE] Processing RFC request. Establishing connection session...")
            # Respond with OPN (Opcode 2 - Connection Opened)
            response_payload = b"ACK_SESSION_ESTABLISHED"
            reply_frame = wrap_oeneye_packet(
                response_payload, 
                opcode=2,  # OPN
                src_addr=self.node_address, 
                dest_addr=int(src, 8)
            )
            print(f"    -> [STATE] Handshake complete. Sent OPN reply frame.")
            return reply_frame
        else:
            print(f"    -> [WARN] Unhandled opcode {opcode}")
            return None

if __name__ == "__main__":
    print("========================================")
    print("   CHAOSNET INTERACTIVE HANDSHAKE SIM")
    print("========================================")
    
    # 1. Initialize Master System and generate outbox frames
    system = OeneyeMasterSystem("oeneye-bootstrap.img")
    system.load_image()
    system.verify_invariants()
    system.map_virtual_memory()
    
    # Grab SUPB segment frame (RFC)
    supb_offset = system.segments["SUPB"]
    payload = bytes(system.virtual_memory[supb_offset : supb_offset + 32])
    rfc_frame = wrap_oeneye_packet(payload, opcode=1, src_addr=0o100, dest_addr=0o200)

    # 2. Initialize Peer Receiver Node at address 0o200
    peer = ChaosnetPeerNode(node_address=0o200)
    
    print("\n[Handshake Exchange Sequence]")
    print("-" * 40)
    opn_reply = peer.handle_incoming_frame(rfc_frame)
    
    # 3. Master Node processes the OPN reply
    if opn_reply:
        master_ack = unwrap_oeneye_packet(opn_reply)
        print(f"\n[Master Node] Received reply from {master_ack['source_address']}:")
        print(f"    - State Status: {master_ack['opcode_name']}")
        print(f"    - Session Payload: {master_ack['payload'].decode('utf-8', errors='ignore')}")
        print("\n[+] Virtual network session active and verified.")
    print("========================================")
