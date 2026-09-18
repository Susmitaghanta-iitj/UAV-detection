from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path

def gen_sequences(outdir: str | Path, sequences: int = 128, taps: int = 32, seed: int = 11):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    manifest=[]
    for s in range(sequences):
        pairs=[]
        sum_qaqw=0
        sum_qa=0
        for _ in range(taps):
            a=rng.randint(0,255)
            w=rng.randint(0,255)
            pairs.append((a,w))
            sum_qaqw += a*w
            sum_qa += a
        manifest.append({
            "seq":s,
            "pairs":pairs,
            "sum_qaqw":sum_qaqw,
            "sum_qa":sum_qa,
        })

    (outdir/"accum_sequences.json").write_text(json.dumps(manifest, indent=2))

    with (outdir/"accum_expected.csv").open("w",newline="") as f:
        wr=csv.writer(f)
        wr.writerow(["seq","sum_qaqw","sum_qa"])
        for m in manifest:
            wr.writerow([m["seq"],m["sum_qaqw"],m["sum_qa"]])

    return manifest

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/mac_coverification")
    ap.add_argument("--sequences",type=int,default=128)
    ap.add_argument("--taps",type=int,default=32)
    ap.add_argument("--seed",type=int,default=11)
    a=ap.parse_args()
    gen_sequences(a.outdir,a.sequences,a.taps,a.seed)
    print(Path(a.outdir)/"accum_sequences.json")

if __name__=="__main__":
    main()
