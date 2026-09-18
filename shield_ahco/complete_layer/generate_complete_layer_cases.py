from __future__ import annotations
import argparse, json, random
from pathlib import Path
from shield_ahco.final_equiv.fixedpoint_metadata import make_fixed_meta
from .complete_layer_reference import LayerQuantMeta, dense_complete, conv1d_complete


def build_common_meta(rng, outputs, frac_bits=24):
    sa=6.0/255.0
    sw=2.0/255.0
    wlow=-1.0
    alpha=6.0
    biases=[rng.uniform(-0.25,0.25) for _ in range(outputs)]
    common=make_fixed_meta(sa,sw,wlow,0.0,alpha,8,frac_bits)
    bias_q=[round(b*(1<<frac_bits)) for b in biases]
    return LayerQuantMeta(
        scale_aw_q=common.scale_aw_q,
        scale_al_q=common.scale_al_q,
        bias_q=bias_q,
        alpha_q=common.alpha_q,
        out_scale_q=common.out_scale_q,
        frac_bits=frac_bits,
    )


def gen_dense(outdir:Path,din=16,dout=4,seed=101):
    rng=random.Random(seed)
    act=[rng.randint(0,255) for _ in range(din)]
    w=[[rng.randint(0,255) for _ in range(din)] for _ in range(dout)]
    meta=build_common_meta(rng,dout)
    y=dense_complete(act,w,meta)

    payload={"din":din,"dout":dout,"act":act,"weight":w,"meta":meta.__dict__,"out_codes":y}
    (outdir/"dense_complete.json").write_text(json.dumps(payload,indent=2))
    with (outdir/"dense_complete_act.mem").open("w") as f:
        for v in act: f.write(f"{v:02x}\n")
    with (outdir/"dense_complete_wgt.mem").open("w") as f:
        for o in range(dout):
            for i in range(din):
                f.write(f"{w[o][i]:02x}\n")
    with (outdir/"dense_complete_bias.mem").open("w") as f:
        for b in meta.bias_q:
            f.write(f"{(b & 0xffffffff):08x}\n")
    with (outdir/"dense_complete_expected.mem").open("w") as f:
        for q in y: f.write(f"{q:02x}\n")
    return payload


def gen_conv(outdir:Path,cin=2,cout=3,length=8,kernel=3,stride=1,padding=1,seed=202):
    rng=random.Random(seed)
    x=[[rng.randint(0,255) for _ in range(length)] for _ in range(cin)]
    w=[[[rng.randint(0,255) for _ in range(kernel)] for _ in range(cin)] for _ in range(cout)]
    meta=build_common_meta(rng,cout)
    y=conv1d_complete(x,w,meta,stride,padding)

    payload={
        "cin":cin,"cout":cout,"length":length,"kernel":kernel,"stride":stride,"padding":padding,
        "input":x,"weight":w,"meta":meta.__dict__,"out_codes":y
    }
    (outdir/"conv_complete.json").write_text(json.dumps(payload,indent=2))
    with (outdir/"conv_complete_input.mem").open("w") as f:
        for ic in range(cin):
            for ix in range(length):
                f.write(f"{x[ic][ix]:02x}\n")
    with (outdir/"conv_complete_wgt.mem").open("w") as f:
        for oc in range(cout):
            for ic in range(cin):
                for k in range(kernel):
                    f.write(f"{w[oc][ic][k]:02x}\n")
    with (outdir/"conv_complete_bias.mem").open("w") as f:
        for b in meta.bias_q:
            f.write(f"{(b & 0xffffffff):08x}\n")
    with (outdir/"conv_complete_expected.mem").open("w") as f:
        for oc in range(cout):
            for ox in range(len(y[oc])):
                f.write(f"{y[oc][ox]:02x}\n")
    return payload


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--outdir",default="vectors/complete_layer")
    args=ap.parse_args()
    out=Path(args.outdir); out.mkdir(parents=True,exist_ok=True)
    d=gen_dense(out)
    c=gen_conv(out)
    print(out/"dense_complete.json")
    print(out/"conv_complete.json")

if __name__=="__main__":
    main()
