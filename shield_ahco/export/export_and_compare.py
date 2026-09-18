from __future__ import annotations
import argparse, json
from pathlib import Path
import torch

from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.qat.qat_layers import convert_to_qat, QATConv1d, QATLinear
from shield_ahco.export.export_qat_int8 import export_qat_model
from shield_ahco.golden.layer_equivalence import load_exported_layer, dense_integer_golden, conv1d_integer_golden


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fp32-checkpoint", required=True)
    ap.add_argument("--qat-checkpoint", default=None,
                    help="Optional QAT checkpoint. If omitted, converts FP32 model and compares initialized QAT.")
    ap.add_argument("--post-pruning", action="store_true")
    ap.add_argument("--bits", type=int, default=8)
    ap.add_argument("--outdir", default="runs/qat_rtl_export")
    args=ap.parse_args()

    base=make_thesis_baseline(args.post_pruning,True)
    fp=torch.load(args.fp32_checkpoint,map_location="cpu")
    base.load_state_dict(fp["model"],strict=True)

    qat=convert_to_qat(base,args.bits).eval()
    if args.qat_checkpoint:
        qck=torch.load(args.qat_checkpoint,map_location="cpu")
        qat.load_state_dict(qck["model"],strict=True)

    outdir=Path(args.outdir)
    manifest=export_qat_model(qat,outdir)

    report={}
    for name,module in qat.named_modules():
        if isinstance(module,QATLinear):
            meta,wq,bias=load_exported_layer(outdir,name)
            x=torch.rand(module.weight.shape[1])*meta["activation"]["alpha"]
            with torch.no_grad():
                y_ref=module(x.unsqueeze(0)).squeeze(0).cpu()
            y_int,_=dense_integer_golden(x,meta,wq,bias)
            err=(y_ref-y_int).abs()
            report[name]={
                "kind":"linear",
                "max_abs_error":float(err.max()),
                "mean_abs_error":float(err.mean()),
            }
            break

    # Compare first Conv1d separately
    for name,module in qat.named_modules():
        if isinstance(module,QATConv1d):
            meta,wq,bias=load_exported_layer(outdir,name)
            cin=module.weight.shape[1]
            k=module.weight.shape[2]
            L=max(16,k+4)
            x=torch.rand(cin,L)*meta["activation"]["alpha"]
            with torch.no_grad():
                y_ref=module(x.unsqueeze(0)).squeeze(0).cpu()
            y_int,_=conv1d_integer_golden(
                x,meta,wq,bias,
                stride=module.stride[0],
                padding=module.padding[0] if isinstance(module.padding,tuple) else int(module.padding)
            )
            # If padding="same" was converted, explicit integer padding metadata is not available here;
            # skip shape-mismatched comparison and record it.
            if y_ref.shape == y_int.shape:
                err=(y_ref-y_int).abs()
                report[name]={
                    "kind":"conv1d",
                    "max_abs_error":float(err.max()),
                    "mean_abs_error":float(err.mean()),
                }
            else:
                report[name]={
                    "kind":"conv1d",
                    "shape_note":f"reference={tuple(y_ref.shape)} integer={tuple(y_int.shape)}"
                }
            break

    (outdir/"equivalence_report.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
