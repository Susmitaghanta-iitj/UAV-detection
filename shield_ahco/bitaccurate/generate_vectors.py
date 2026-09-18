import argparse, csv, random
from pathlib import Path
from .fixed import FXP8_Q34, encode as fx_encode
from .posit import POSIT4_1, decode_bits as pdecode
from .mac import dot_fxp8_q34, dot_posit

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors")
    ap.add_argument("--random",type=int,default=1000)
    ap.add_argument("--seed",type=int,default=7)
    a=ap.parse_args()
    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    with (out/"posit4_1_decode.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["code","value"])
        for c in range(16): w.writerow([c,pdecode(c,POSIT4_1)])
    with (out/"posit4_1_mul.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["a_code","b_code","out_code","out_value"])
        for ac in range(16):
            for bc in range(16):
                av,bv=pdecode(ac,POSIT4_1),pdecode(bc,POSIT4_1)
                if av!=av or bv!=bv: continue
                r=dot_posit([av],[bv],POSIT4_1); w.writerow([ac,bc,r.code,r.decoded])
    rng=random.Random(a.seed)
    with (out/"fxp8_q34_random_mac.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["x","w","x_code","w_code","acc_raw","out_value"])
        for _ in range(a.random):
            x=rng.uniform(-8,7.9375); y=rng.uniform(-8,7.9375); r=dot_fxp8_q34([x],[y])
            w.writerow([x,y,fx_encode(x,FXP8_Q34),fx_encode(y,FXP8_Q34),r.accumulator_raw,r.decoded])
if __name__=="__main__": main()
