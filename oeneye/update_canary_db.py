"""
OeneyeDB Canary Integrator - APPEND SAFE
"""
import hashlib, pathlib, os, datetime
base = pathlib.Path.home() / "oeneye"
os.chdir(base if base.exists() else pathlib.Path.cwd())

def h(p): 
    try: return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
    except: return "0"*64

db = pathlib.Path("oeneyeOS/oeneyeDB/config.conf")
fnt = h("OMQ.FNT")
canary = h("CANARY.txt")
canary_short = h("CANARY.txt")[:12]

# keep original seal, append new registry
entry = f"\n# --- {datetime.date.today().isoformat()} CANARY INTEGRATION ---\nCANARY_HASH={canary}\nCANARY_SHORT={canary_short}\nOMQ_FNT_HASH={fnt}\nSIGNATURE=36883:dbOENEYE bccd0ccf90f9e23bf7c98867ea12acf3049babb32\n"

# restore original if you overwrote it, then append
if "dbOENEYE Canary Registry" in db.read_text():
    print("[!] You overwrote the seal - restoring from git")
    os.system("git checkout -- oeneyeOS/oeneyeDB/config.conf 2>/dev/null || git restore oeneyeOS/oeneyeDB/config.conf")

with db.open("a") as f:
    f.write(entry)

print(f"[+] Appended to {db}")
print(entry)
