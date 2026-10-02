import os, hashlib, pathlib
def sha256(p):
    try: return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:12]
    except: return "MISSING"
def render_status():
    print(f"""
       o∞o  OENEYE ECOSYSTEM STATUS  o∞o

  [!] CANARY CHANNEL : STABLE (0x8000)
  [~] DEV CHANNEL    : ACTIVE (FS MAPPED)
  [*] CORE BRAND     : ONLINE [o∞o]

  OMQ.FNT            : {sha256('OMQ.FNT')}... 4096
  oeneyeDB config    : {sha256('oeneyeOS/oeneyeDB/config.conf')}... 36883:dbOENEYE
  main               : 38b9d9f -> origin/main OK
  ns-holla           : origin/ns-holla OK
  CANARY.txt         : {sha256('CANARY.txt')}...

""")
if __name__ == "__main__": render_status()
