from __future__ import annotations
import argparse
from pathlib import Path

def check(path,prefix):
    total=0;mm=[]
    for line in Path(path).read_text().splitlines():
        if not line.startswith(prefix): continue
        f=dict(x.split("=") for x in line.split()[1:])
        total+=1
        if int(f["out"])!=int(f["exp"]):
            mm.append(line)
    return total,mm

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dense-log")
    ap.add_argument("--conv-log")
    a=ap.parse_args()
    fail=False
    if a.dense_log:
        n,mm=check(a.dense_log,"DENSE ")
        print("dense",n,"mismatches",len(mm))
        for x in mm[:20]: print(x)
        fail|=bool(mm)
    if a.conv_log:
        n,mm=check(a.conv_log,"CONV ")
        print("conv",n,"mismatches",len(mm))
        for x in mm[:20]: print(x)
        fail|=bool(mm)
    raise SystemExit(1 if fail else 0)

if __name__=="__main__":
    main()
