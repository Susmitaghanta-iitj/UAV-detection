from __future__ import annotations
import argparse, json, random
from pathlib import Path

def generate_case(outdir: str | Path, din: int = 32, dout: int = 8, seed: int = 13):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    act = [rng.randint(0,255) for _ in range(din)]
    weight = [[rng.randint(0,255) for _ in range(din)] for _ in range(dout)]

    expected=[]
    sum_qa = sum(act)
    for o in range(dout):
        sum_qaqw = sum(act[i]*weight[o][i] for i in range(din))
        expected.append({"o":o,"sum_qaqw":sum_qaqw,"sum_qa":sum_qa})

    payload={
        "din":din,
        "dout":dout,
        "seed":seed,
        "act":act,
        "weight":weight,
        "expected":expected
    }
    (outdir/"dense_case.json").write_text(json.dumps(payload, indent=2))

    with (outdir/"dense_act.mem").open("w") as f:
        for a in act:
            f.write(f"{a:02x}\n")

    with (outdir/"dense_weight.mem").open("w") as f:
        for o in range(dout):
            for i in range(din):
                f.write(f"{weight[o][i]:02x}\n")

    with (outdir/"dense_expected.txt").open("w") as f:
        for e in expected:
            f.write(f"{e['o']} {e['sum_qaqw']} {e['sum_qa']}\n")

    return payload

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/layer_coverification")
    ap.add_argument("--din",type=int,default=32)
    ap.add_argument("--dout",type=int,default=8)
    ap.add_argument("--seed",type=int,default=13)
    a=ap.parse_args()
    generate_case(a.outdir,a.din,a.dout,a.seed)
    print(Path(a.outdir)/"dense_case.json")

if __name__=="__main__":
    main()
