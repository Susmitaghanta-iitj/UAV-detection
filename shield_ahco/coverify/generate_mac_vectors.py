from __future__ import annotations
import argparse, csv, json, random
from pathlib import Path

def gen_vectors(outdir: str | Path, n: int = 1000, seed: int = 7,
                act_bits: int = 8, wgt_bits: int = 8):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    max_a = (1 << act_bits) - 1
    max_w = (1 << wgt_bits) - 1

    rows = []
    for idx in range(n):
        a = rng.randint(0, max_a)
        w = rng.randint(0, max_w)
        prod = a * w
        rows.append((idx, a, w, prod))

    csv_path = outdir / "mac_vectors.csv"
    with csv_path.open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["idx","act_code","wgt_code","product"])
        wr.writerows(rows)

    # Hex files for testbench $readmemh
    with (outdir/"act.mem").open("w") as fa, (outdir/"wgt.mem").open("w") as fw, (outdir/"prod.mem").open("w") as fp:
        for _,a,w,p in rows:
            fa.write(f"{a:02x}\n")
            fw.write(f"{w:02x}\n")
            fp.write(f"{p:04x}\n")

    meta = {
        "num_vectors": n,
        "seed": seed,
        "act_bits": act_bits,
        "wgt_bits": wgt_bits,
    }
    (outdir/"meta.json").write_text(json.dumps(meta, indent=2))
    return csv_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="vectors/mac_coverification")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    p = gen_vectors(args.outdir, args.n, args.seed)
    print(p)

if __name__ == "__main__":
    main()
