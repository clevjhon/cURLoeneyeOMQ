import sys,math
def analyze(p):
    from collections import Counter
    import os
    size=os.path.getsize(p)
    sample=10*1024*1024
    cnt=[0]*256; tot=0
    with open(p,'rb') as f:
        while tot<sample:
            d=f.read(1024*1024)
            if not d: break
            tot+=len(d)
            for i in range(256): cnt[i]+=d.count(i)
    ent=0.0
    for c in cnt:
        if c:
            pr=c/tot
            ent-=pr*math.log2(pr)
    print(f"File: {p} ({size} bytes, checked {tot})")
    print(f"Entropy: {ent:.4f}/8.0 = {ent/8*100:.2f}%")
    print("HIGH (encrypted)" if ent>7.0 else "LOW (text)")
if __name__=='__main__':
    analyze(sys.argv[1] if len(sys.argv)>1 else 'termuxDB.bin')
