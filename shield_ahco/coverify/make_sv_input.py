from __future__ import annotations
import argparse,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",default="vectors/mac_coverification/accum_sequences.json")
    ap.add_argument("--out",default="vectors/mac_coverification/accum_sequences_flat.txt")
    args=ap.parse_args()

    data=json.loads(Path(args.json).read_text())
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w") as f:
        for m in data:
            f.write(f"{m['seq']} {len(m['pairs'])}\n")
            for a,w in m["pairs"]:
                f.write(f"{a} {w}\n")
    print(out)

if __name__=="__main__":
    main()
