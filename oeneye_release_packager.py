import tarfile
import os

class ReleasePackager:
    def __init__(self, output_tar="oeneye_release_v1.0.tar.gz"):
        self.output_tar = output_tar
        self.files_to_pack = [
            "oeneye-compiled.img",
            "oeneye_monograph.tex",
            "oeneye_zenodo_payload.json",
            "index.html",
            "oeneye_deployment_audit.log"
        ]

    def package(self):
        print("========================================")
        print("   OENEYE RELEASE ARCHIVER")
        print("========================================")
        
        with tarfile.open(self.output_tar, "w:gz") as tar:
            for file in self.files_to_pack:
                if os.path.exists(file):
                    tar.add(file)
                    print(f"[+] Added to archive: {file}")
                else:
                    print(f"[!] Warning: '{file}' not found, skipping.")

        print(f"[+] Complete release package created: '{self.output_tar}'")
        print("========================================")

if __name__ == "__main__":
    packager = ReleasePackager()
    packager.package()
