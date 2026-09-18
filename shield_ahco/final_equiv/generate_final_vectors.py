from __future__ import annotations
import argparse, json, random
from pathlib import Path
from .fixedpoint_metadata import make_fixed_meta
from .finalize_reference import exact_finalize, fixed_finalize

def generate(outdir: str | Path, n: int = 512, seed: int = 23, frac_bits: int = 24):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    rng=random.Random(seed)
    rows=[]

    # Representative learned-quantizer metadata.
    # These are synthetic regression constants, not claimed as source-trained values.
    sa=6.0/255.0
    sw=2.0/255.0
    wlow=-1.0
    alpha=6.0

    for idx in range(n):
        taps=rng.randint(1,64)
        sum_qa=sum(rng.randint(0,255) for _ in range(taps))
        sum_qaqw=sum(rng.randint(0,255)*rng.randint(0,255) for _ in range(taps))
        bias=rng.uniform(-0.5,0.5)

        meta=make_fixed_meta(sa,sw,wlow,bias,alpha,8,frac_bits)
        exact=exact_finalize(sum_qaqw,sum_qa,sa,sw,wlow,bias,alpha,8)
        fixed=fixed_finalize(sum_qaqw,sum_qa,meta,8)

        rows.append({
            "idx":idx,
            "sum_qaqw":sum_qaqw,
            "sum_qa":sum_qa,
            "bias":bias,
            "scale_aw_q":meta.scale_aw_q,
            "scale_al_q":meta.scale_al_q,
            "bias_q":meta.bias_q,
            "alpha_q":meta.alpha_q,
            "out_scale_q":meta.out_scale_q,
            "exact_out_code":exact.out_code,
            "fixed_out_code":fixed.out_code,
            "exact_preact":exact.preact_float,
            "fixed_preact":fixed.preact_float,
        })

    (outdir/"final_vectors.json").write_text(json.dumps(rows,indent=2))
    with (outdir/"final_vectors.txt").open("w") as f:
        for r in rows:
            f.write(
                f"{r['idx']} {r['sum_qaqw']} {r['sum_qa']} "
                f"{r['scale_aw_q']} {r['scale_al_q']} {r['bias_q']} "
                f"{r['alpha_q']} {r['out_scale_q']} {r['fixed_out_code']}\n"
            )
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/final_output_equivalence")
    ap.add_argument("--n",type=int,default=512)
    ap.add_argument("--seed",type=int,default=23)
    ap.add_argument("--frac-bits",type=int,default=24)
    a=ap.parse_args()
    rows=generate(a.outdir,a.n,a.seed,a.frac_bits)
    mismatches=sum(r["exact_out_code"]!=r["fixed_out_code"] for r in rows)
    print(Path(a.outdir)/"final_vectors.json")
    print("exact-vs-fixed code mismatches:",mismatches,"/",len(rows))

if __name__=="__main__":
    main()
