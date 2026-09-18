from __future__ import annotations
import argparse, json, random
from pathlib import Path

def generate_case(outdir: str | Path, cin: int = 2, cout: int = 3,
                  length: int = 16, kernel: int = 3, stride: int = 1,
                  padding: int = 1, seed: int = 17):
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    rng=random.Random(seed)

    x=[[rng.randint(0,255) for _ in range(length)] for _ in range(cin)]
    w=[[[rng.randint(0,255) for _ in range(kernel)] for _ in range(cin)] for _ in range(cout)]

    out_len=((length+2*padding-kernel)//stride)+1
    expected=[]
    for oc in range(cout):
        for ox in range(out_len):
            sum_qaqw=0
            sum_qa=0
            for ic in range(cin):
                for k in range(kernel):
                    ix=ox*stride+k-padding
                    qa=x[ic][ix] if 0<=ix<length else 0
                    qw=w[oc][ic][k]
                    sum_qaqw += qa*qw
                    sum_qa += qa
            expected.append({
                "oc":oc,"ox":ox,
                "sum_qaqw":sum_qaqw,
                "sum_qa":sum_qa
            })

    payload={
        "cin":cin,"cout":cout,"length":length,"kernel":kernel,
        "stride":stride,"padding":padding,"seed":seed,
        "input":x,"weight":w,"expected":expected
    }
    (outdir/"conv_case.json").write_text(json.dumps(payload,indent=2))

    with (outdir/"conv_input.mem").open("w") as f:
        for ic in range(cin):
            for ix in range(length):
                f.write(f"{x[ic][ix]:02x}\n")

    with (outdir/"conv_weight.mem").open("w") as f:
        for oc in range(cout):
            for ic in range(cin):
                for k in range(kernel):
                    f.write(f"{w[oc][ic][k]:02x}\n")

    with (outdir/"conv_expected.txt").open("w") as f:
        for e in expected:
            f.write(f"{e['oc']} {e['ox']} {e['sum_qaqw']} {e['sum_qa']}\n")

    return payload

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/layer_coverification")
    ap.add_argument("--cin",type=int,default=2)
    ap.add_argument("--cout",type=int,default=3)
    ap.add_argument("--length",type=int,default=16)
    ap.add_argument("--kernel",type=int,default=3)
    ap.add_argument("--stride",type=int,default=1)
    ap.add_argument("--padding",type=int,default=1)
    ap.add_argument("--seed",type=int,default=17)
    a=ap.parse_args()
    generate_case(a.outdir,a.cin,a.cout,a.length,a.kernel,a.stride,a.padding,a.seed)
    print(Path(a.outdir)/"conv_case.json")

if __name__=="__main__":
    main()
