from __future__ import annotations
import argparse, json, random
from pathlib import Path
from shield_ahco.final_equiv.fixedpoint_metadata import make_fixed_meta
from shield_ahco.complete_layer.complete_layer_reference import LayerQuantMeta
from .block_reference import conv_pool_block


def make_meta(rng, outputs, frac_bits=24):
    sa=6.0/255.0
    sw=2.0/255.0
    wlow=-1.0
    alpha=6.0
    common=make_fixed_meta(sa,sw,wlow,0.0,alpha,8,frac_bits)
    bias_q=[round(rng.uniform(-0.25,0.25)*(1<<frac_bits)) for _ in range(outputs)]
    return LayerQuantMeta(
        scale_aw_q=common.scale_aw_q,
        scale_al_q=common.scale_al_q,
        bias_q=bias_q,
        alpha_q=common.alpha_q,
        out_scale_q=common.out_scale_q,
        frac_bits=frac_bits,
    )


def gen(outdir: str|Path, seed=303):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    rng=random.Random(seed)

    # Small co-verification proxy for first two CNN blocks.
    # Structure mirrors Conv -> Pool -> Conv -> Pool reuse,
    # not the full source dimensions.
    cin1, cout1, length1, k1, p1 = 1, 4, 32, 3, 2
    cin2, cout2, k2, p2 = cout1, 3, 3, 2

    x=[rng.randint(0,255) for _ in range(cin1*length1)]
    w1=[[[rng.randint(0,255) for _ in range(k1)] for _ in range(cin1)] for _ in range(cout1)]
    m1=make_meta(rng,cout1)

    c1,pool1,c1len,p1len=conv_pool_block(
        x,w1,m1,cin1,cout1,length1,k1,p1,stride=1,padding=1
    )

    w2=[[[rng.randint(0,255) for _ in range(k2)] for _ in range(cin2)] for _ in range(cout2)]
    m2=make_meta(rng,cout2)
    c2,pool2,c2len,p2len=conv_pool_block(
        pool1,w2,m2,cin2,cout2,p1len,k2,p2,stride=1,padding=1
    )

    payload={
        "block1":{
            "cin":cin1,"cout":cout1,"length":length1,"kernel":k1,"pool":p1,
            "input":x,"weight":w1,"meta":m1.__dict__,
            "conv_out":c1,"pool_out":pool1,"conv_len":c1len,"pool_len":p1len
        },
        "block2":{
            "cin":cin2,"cout":cout2,"length":p1len,"kernel":k2,"pool":p2,
            "input":pool1,"weight":w2,"meta":m2.__dict__,
            "conv_out":c2,"pool_out":pool2,"conv_len":c2len,"pool_len":p2len
        }
    }
    (outdir/"two_block_case.json").write_text(json.dumps(payload,indent=2))

    # Flat memories for RTL proxy
    with (outdir/"input.mem").open("w") as f:
        for v in x: f.write(f"{v:02x}\n")
    for bid,(w,m) in enumerate([(w1,m1),(w2,m2)],1):
        with (outdir/f"w{bid}.mem").open("w") as f:
            for oc in range(len(w)):
                for ic in range(len(w[oc])):
                    for k in range(len(w[oc][ic])):
                        f.write(f"{w[oc][ic][k]:02x}\n")
        with (outdir/f"b{bid}.mem").open("w") as f:
            for b in m.bias_q: f.write(f"{(b & 0xffffffff):08x}\n")

    with (outdir/"block1_pool_expected.mem").open("w") as f:
        for v in pool1: f.write(f"{v:02x}\n")
    with (outdir/"block2_pool_expected.mem").open("w") as f:
        for v in pool2: f.write(f"{v:02x}\n")

    return payload


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/cnn_block")
    ap.add_argument("--seed",type=int,default=303)
    a=ap.parse_args()
    p=gen(a.outdir,a.seed)
    print(Path(a.outdir)/"two_block_case.json")
    print("block1 pooled elements:",len(p["block1"]["pool_out"]))
    print("block2 pooled elements:",len(p["block2"]["pool_out"]))

if __name__=="__main__":
    main()
