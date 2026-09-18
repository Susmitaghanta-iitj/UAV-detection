from __future__ import annotations
import argparse, json
from pathlib import Path
import torch
from torch.utils.data import DataLoader, random_split

from ..dataset import UAVAudioDataset
from ..features import AudioConfig
from ..model_1dfcnn import ModelConfig, Shield1DFCNN
from .quant_layers import quantize_model
from .bose8 import collect_gradient_sensitivity, make_bose8_assignment, apply_layer_assignment


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct = total = tp = fp = fn = 0
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        p = model(x).argmax(1)
        correct += int((p == y).sum())
        total += y.numel()
        tp += int(((p == 1) & (y == 1)).sum())
        fp += int(((p == 1) & (y == 0)).sum())
        fn += int(((p == 0) & (y == 1)).sum())
    acc = correct / max(total, 1)
    prec = tp / max(tp+fp, 1)
    rec = tp / max(tp+fn, 1)
    f1 = 2*prec*rec/max(prec+rec, 1e-12)
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--bose-low-fraction", type=float, default=0.5)
    ap.add_argument("--out", default="runs/precision_sweep.json")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load(args.checkpoint, map_location="cpu")
    feature = ckpt.get("feature", "mfcc")
    ds = UAVAudioDataset(args.data_root, feature, AudioConfig())

    n_train = int(0.8 * len(ds))
    n_val = int(0.1 * len(ds))
    n_test = len(ds)-n_train-n_val
    train_ds, val_ds, test_ds = random_split(
        ds, [n_train,n_val,n_test],
        generator=torch.Generator().manual_seed(args.seed)
    )
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False)

    model = Shield1DFCNN(ckpt["input_length"], ModelConfig())
    model.load_state_dict(ckpt["model"])
    model = model.to(device).eval()

    precisions = [
        "fp32",
        "bf16",
        "int8",
        "fxp8_q34",
        "posit8_2",
        "hfp4_e2m1",
        "hfp4_e3m0",
        "posit4_1",
    ]

    results = {}
    for p in precisions:
        qm = model if p == "fp32" else quantize_model(model, p, quantize_activation=True).to(device)
        results[p] = evaluate(qm, test_loader, device)
        print(p, results[p])

    sens = collect_gradient_sensitivity(
        model, train_loader, device=device, max_batches=8, low_precision="posit4_1"
    )
    assignment = make_bose8_assignment(
        sens,
        low_fraction=args.bose_low_fraction,
        low_precision="posit4_1",
        high_precision="posit8_2",
    )
    bose_model = apply_layer_assignment(model, assignment, quantize_activation=True).to(device)
    results["bose8"] = evaluate(bose_model, test_loader, device)
    results["bose8_assignment"] = assignment
    results["sensitivity"] = [{"name": s.name, "score": s.score} for s in sens]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
