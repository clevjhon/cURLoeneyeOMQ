"""
Chaosnet packet encoder/decoder
================================
Implements the software-level packet header of Chaosnet, the local-area
network protocol developed at MIT's AI Lab (1973-1975) for Lisp Machines
and ITS, as documented in David Moon's "Chaosnet" (AI Memo 628, 1981) and
summarized at https://gunkies.org/wiki/Chaosnet.

This implements the LOGICAL software packet format (the 8x 16-bit header
words + data, as software on both ends actually manipulates it) -- not the
physical wire-level bit ordering of the original 1970s hardware transceivers
(which reversed/framed bits in ways specific to that now-extinct hardware).
That distinction is called out explicitly in the source material and is not
something a software-only encoder/decoder needs to reproduce to be a
faithful implementation of the *protocol*.

Header layout (8 words, 16 bits each):
    Word 0: Opcode            (high byte)   | unused, always 0 (low byte)
    Word 1: Forwarding count  (high nibble) | Payload length in bytes (12 bits)
    Word 2: Source address
    Word 3: Source index
    Word 4: Destination address
    Word 5: Destination index
    Word 6: Packet number
    Word 7: Acknowledgement

Followed by 0-488 bytes of payload data (the historical max packet size).
"""
import struct
from dataclasses import dataclass, field

HEADER_WORDS = 8
HEADER_SIZE = HEADER_WORDS * 2   # 16 bytes
MAX_PAYLOAD = 488                # historical Chaosnet packet size limit

# ---- Packet opcodes (from Moon 1981 / gunkies.org) ----
OPCODES = {
    1:  "RFC",   # request for connection
    2:  "OPN",   # connection opened
    3:  "CLS",   # connection closed
    4:  "FWD",   # connection forwarded
    5:  "ANS",   # answer
    6:  "SNS",   # sense status
    7:  "STS",   # status
    8:  "RUT",   # routing information (decimal 8 == octal 10 in Moon's memo)
    9:  "LOS",   # lossage
    10: "LSN",   # listen for connection
    11: "MNT",   # maintenance
    12: "EOF",   # end of file
    13: "UNC",   # uncontrolled packet
    14: "BRD",   # broadcast packet
    # 200 (octal 310) and up: DAT, connection data -- represented as a range below
}
DAT_MIN = 200  # decimal; "DAT, connection data" per the spec table (200 and up)

NAME_TO_OPCODE = {v: k for k, v in OPCODES.items()}


def opcode_name(opcode: int) -> str:
    if opcode in OPCODES:
        return OPCODES[opcode]
    if opcode >= DAT_MIN:
        return "DAT"
    return f"UNKNOWN(0x{opcode:02x})"


@dataclass
class ChaosPacket:
    opcode: int
    source_addr: int
    source_index: int
    dest_addr: int
    dest_index: int
    packet_number: int = 0
    ack: int = 0
    forwarding_count: int = 0
    data: bytes = field(default_factory=bytes)

    def __post_init__(self):
        if len(self.data) > MAX_PAYLOAD:
            raise ValueError(f"payload of {len(self.data)} bytes exceeds "
                              f"the {MAX_PAYLOAD}-byte Chaosnet packet limit")
        for name, val, bits in [
            ("opcode", self.opcode, 8), ("source_addr", self.source_addr, 16),
            ("source_index", self.source_index, 16), ("dest_addr", self.dest_addr, 16),
            ("dest_index", self.dest_index, 16), ("packet_number", self.packet_number, 16),
            ("ack", self.ack, 16), ("forwarding_count", self.forwarding_count, 4),
        ]:
            if not (0 <= val < (1 << bits)):
                raise ValueError(f"{name}={val} doesn't fit in {bits} bits")

    @property
    def opcode_name(self) -> str:
        return opcode_name(self.opcode)


def encode(pkt: ChaosPacket) -> bytes:
    """Pack a ChaosPacket into its 16-byte header + payload, matching the
    field layout documented for Chaosnet's software packet format."""
    word0 = (pkt.opcode & 0xFF) << 8              # opcode in high byte, low byte 0
    word1 = ((pkt.forwarding_count & 0xF) << 12) | (len(pkt.data) & 0xFFF)
    header = struct.pack(
        ">HHHHHHHH",
        word0,
        word1,
        pkt.source_addr,
        pkt.source_index,
        pkt.dest_addr,
        pkt.dest_index,
        pkt.packet_number,
        pkt.ack,
    )
    # Chaosnet pads the data region to an even number of bytes
    payload = pkt.data
    if len(payload) % 2:
        payload += b"\x00"
    return header + payload


def decode(raw: bytes) -> ChaosPacket:
    """Parse raw bytes back into a ChaosPacket, validating the length field."""
    if len(raw) < HEADER_SIZE:
        raise ValueError(f"packet too short: {len(raw)} bytes, need at least {HEADER_SIZE}")
    words = struct.unpack(">HHHHHHHH", raw[:HEADER_SIZE])
    word0, word1, src_addr, src_idx, dst_addr, dst_idx, pktnum, ack = words

    opcode = (word0 >> 8) & 0xFF
    forwarding_count = (word1 >> 12) & 0xF
    payload_len = word1 & 0xFFF

    payload_region = raw[HEADER_SIZE:]
    if len(payload_region) < payload_len:
        raise ValueError(f"declared payload length {payload_len} exceeds "
                          f"actual remaining bytes {len(payload_region)}")
    data = payload_region[:payload_len]

    return ChaosPacket(
        opcode=opcode, source_addr=src_addr, source_index=src_idx,
        dest_addr=dst_addr, dest_index=dst_idx, packet_number=pktnum,
        ack=ack, forwarding_count=forwarding_count, data=data,
    )


def hexdump(raw: bytes) -> str:
    lines = []
    for i in range(0, len(raw), 16):
        chunk = raw[i:i+16]
        hexpart = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:04x}: {hexpart:<47s} |{ascii_part}|")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Demonstration
# --------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("Chaosnet packet encoder/decoder -- demonstration")
    print("=" * 70)

    # Example 1: an RFC (request for connection) -- what a client sends to
    # open a connection to a named contact (service) on a remote host.
    rfc = ChaosPacket(
        opcode=NAME_TO_OPCODE["RFC"],
        source_addr=0o101,     # host addresses were traditionally written in octal
        source_index=1,
        dest_addr=0o202,
        dest_index=0,
        packet_number=1,
        data=b"TELNET",        # the contact name being requested
    )
    encoded = encode(rfc)
    print(f"\n[1] RFC packet ({rfc.opcode_name}, requesting contact "
          f"{rfc.data.decode()!r}):")
    print(hexdump(encoded))

    decoded = decode(encoded)
    print(f"  -> decoded: opcode={decoded.opcode_name} "
          f"src={oct(decoded.source_addr)}#{decoded.source_index} "
          f"dst={oct(decoded.dest_addr)}#{decoded.dest_index} "
          f"data={decoded.data!r}")
    assert decoded == rfc, "round-trip mismatch!"

    # Example 2: a DAT (connection data) packet carrying an actual payload.
    dat = ChaosPacket(
        opcode=DAT_MIN,
        source_addr=0o202,
        source_index=5,
        dest_addr=0o101,
        dest_index=1,
        packet_number=42,
        ack=41,
        data=b"Hello from a Lisp Machine, 1978.",
    )
    encoded2 = encode(dat)
    print(f"\n[2] DAT packet ({dat.opcode_name}, carrying "
          f"{len(dat.data)} bytes of data):")
    print(hexdump(encoded2))

    decoded2 = decode(encoded2)
    print(f"  -> decoded: opcode={decoded2.opcode_name} "
          f"pkt#={decoded2.packet_number} ack={decoded2.ack} "
          f"data={decoded2.data!r}")
    assert decoded2.data.rstrip(b"\x00") == dat.data, "round-trip mismatch!"

    # Example 3: a truncated/corrupt packet is correctly rejected.
    print("\n[3] Error handling -- feeding a truncated packet:")
    try:
        decode(encoded2[:10])
    except ValueError as e:
        print(f"  -> correctly rejected: {e}")

    print("\nAll round-trips verified byte-for-byte. Opcode table:")
    for code, name in sorted(OPCODES.items()):
        print(f"  {code:3d}  {name}")
    print(f"  {DAT_MIN:3d}+ DAT  (connection data)")
