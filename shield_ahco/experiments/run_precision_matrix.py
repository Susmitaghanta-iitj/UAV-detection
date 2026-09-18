from __future__ import annotations
import argparse, json
from pathlib import Path
import torch
from torch.utils.data import DataLoader, random_split

from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.training.train_thesis_waveform import WaveformUAVDataset, evaluate
from shield_ahco.experiments.quantized_model import quantize_source_model
from shield_ahco.experiments.precision_metadata import PRECISIONS, parameter_storage_bytes, compression_vs_fp32
from shield_ahco.pruning.structured_channel_pruning import count_conv_macs, dense_macs


def param_count(m):
    return sum(p.numel() for p in m.parameters())


def make_model(post_pruning: bool):
    return make_thesis_baseline(post_pruning=post_pruning, reconcile_pruning_claim=True)


def load_checkpoint_if_given(model, ckpt_path):
    if ckpt_path is None:
        return model
    ck = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(ck["model"], strict=True)
    return model


def estimate_serial_cycles(model, macs_per_cycle=1):
    # conservative single-MAC serialized estimate
    total_macs = count_conv_macs(model, 35280) + dense_macs(model)
    return (total_macs + macs_per_cycle - 1)//macs_per_cycle


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--baseline-checkpoint", default=None)
    ap.add_argument("--reduced-checkpoint", default=None)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--max-samples", type=int, default=0,
                    help="0 means full test split; use small value for quick smoke evaluation")
    ap.add_argument("--out", default="runs/precision_matrix.json")
    args=ap.parse_args()

    device="cuda" if torch.cuda.is_available() else "cpu"
    ds=WaveformUAVDataset(args.data_root)
    ntr=int(.8*len(ds)); nv=int(.1*len(ds)); nt=len(ds)-ntr-nv
    tr,va,te=random_split(ds,[ntr,nv,nt],generator=torch.Generator().manual_seed(args.seed))
    if args.max_samples and args.max_samples < len(te):
        te=torch.utils.data.Subset(te, range(args.max_samples))
    test_loader=DataLoader(te,batch_size=args.batch_size)

    configs = {
        "baseline_35072": (False, args.baseline_checkpoint),
        "reduced_8704": (True, args.reduced_checkpoint),
    }

    precisions = [
        "fp32","bf16","int8","fxp8_q34",
        "posit8_2","posit4_1","hfp4_e2m1","hfp4_e3m0"
    ]

    results={}
    for cname,(post,ckpt) in configs.items():
        base=make_model(post)
        base=load_checkpoint_if_given(base,ckpt).to(device).eval()

        pc=param_count(base)
        conv=count_conv_macs(base,35280)
        dense=dense_macs(base)
        cfg={
            "flatten_dim": base.flatten_dim,
            "feature_shape": list(base.feature_shape),
            "param_count": pc,
            "conv_macs": conv,
            "dense_macs": dense,
            "total_macs": conv+dense,
            "serialized_mac_cycles_1lane": estimate_serial_cycles(base,1),
            "precisions": {}
        }

        for p in precisions:
            qm=quantize_source_model(base,p,quantize_activation=True).to(device).eval()
            met=evaluate(qm,test_loader,device)
            cfg["precisions"][p]={
                **met,
                "bits": PRECISIONS[p].bits,
                "family": PRECISIONS[p].family,
                "ideal_parameter_storage_bytes": parameter_storage_bytes(pc,p),
                "ideal_parameter_storage_mb": parameter_storage_bytes(pc,p)/(1024**2),
                "ideal_compression_vs_fp32": compression_vs_fp32(p),
            }
            print(cname,p,cfg["precisions"][p])

        results[cname]=cfg

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))

if __name__=="__main__":
    main()
