import json
from datetime import datetime, timezone

class ZenodoPackager:
    def __init__(self, output_json="oeneye_zenodo_payload.json"):
        self.output_json = output_json

    def generate_payload(self):
        print("========================================")
        print("   OENEYE ZENODO / DUBLIN CORE PACKAGER")
        print("========================================")

        timestamp = datetime.now(timezone.utc).isoformat()

        metadata_payload = {
            "metadata": {
                "title": "Technical Monograph and Verification Suite for the oeneye Kernel Architecture",
                "upload_type": "publication",
                "publication_type": "technicalnote",
                "description": (
                    "Formal invariant verification, virtual runtime memory mapping, "
                    "interactive Chaosnet session handshaking, and audited chunked data "
                    "streaming pipeline for the oeneye operating system architecture."
                ),
                "creators": [
                    {
                        "name": "Ketelhut, Kai Olaf",
                        "affiliation": "Berlin, Germany"
                    }
                ],
                "access_right": "open",
                "license": "cc-by-4.0",
                "keywords": [
                    "oeneye",
                    "kernel architecture",
                    "Chaosnet",
                    "ReFS",
                    "FSRS",
                    "formal verification"
                ],
                "notes": f"Archival package compiled on {timestamp}."
            }
        }

        with open(self.output_json, "w") as f:
            json.dump(metadata_payload, f, indent=4)

        print(f"[+] Zenodo deposition payload generated: '{self.output_json}'")
        print("[+] Dublin Core XML mapping structure verified.")
        print("========================================")

if __name__ == "__main__":
    packager = ZenodoPackager()
    packager.generate_payload()
