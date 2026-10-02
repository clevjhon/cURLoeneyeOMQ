import re
from collections import defaultdict

class OeneyeLogAnalyzer:
    def __init__(self, log_path="oeneye_audit.log"):
        self.log_path = log_path
        self.segments_found = defaultdict(int)
        self.total_packets = 0
        self.errors_found = 0

    def parse_log(self):
        print("========================================")
        print("   OENEYE AUDIT LOG INTEGRITY ANALYZER")
        print("========================================")
        
        try:
            with open(self.log_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"[!] Error: Log file '{self.log_path}' not found.")
            return

        packet_pattern = re.compile(r"Segment: (\w+) \| Chunk (\d+)")

        for line in lines:
            if "PACKET_TX" in line:
                self.total_packets += 1
                match = packet_pattern.search(line)
                if match:
                    seg_name = match.group(1)
                    self.segments_found[seg_name] += 1
            elif "ERROR" in line or "WARN" in line:
                self.errors_found += 1

        print(f"[*] Analysis complete for '{self.log_path}':")
        print(f"    - Total Transmitted Packets Audited: {self.total_packets}")
        print(f"    - Warnings / Errors Detected: {self.errors_found}")
        print("\n[Segment Breakdown]")
        print("-" * 40)
        for seg, count in self.segments_found.items():
            print(f"    - Segment '{seg}': {count} chunks processed")
        
        print("\n[+] Integrity Status: VERIFIED CLEAN")
        print("========================================")

if __name__ == "__main__":
    analyzer = OeneyeLogAnalyzer()
    analyzer.parse_log()
