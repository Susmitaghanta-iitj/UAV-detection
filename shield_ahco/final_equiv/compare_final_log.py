from __future__ import annotations
import argparse
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--log",default="vectors/final_output_equivalence/final_rtl.log")
    a=ap.parse_args()

    total=0; mismatches=[]
    for line in Path(a.log).read_text().splitlines():
        if not line.startswith("FINAL "): continue
        f=dict(x.split("=") for x in line.split()[1:])
        total += 1
        if int(f["out"]) != int(f["expected"]):
            mismatches.append((int(f["idx"]),int(f["out"]),int(f["expected"])))
    print(f"finalizer total={total} mismatches={len(mismatches)}")
    for m in mismatches[:20]: print("MISMATCH",m)
    raise SystemExit(1 if mismatches else 0)

if __name__=="__main__":
    main()
