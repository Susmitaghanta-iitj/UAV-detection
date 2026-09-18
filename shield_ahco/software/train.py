from __future__ import annotations
import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch import nn
from torch.utils.data import DataLoader, random_split

from .dataset import UAVAudioDataset
from .features import AudioConfig
from .model_1dfcnn import ModelConfig, Shield1DFCNN


def seed_all(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def metrics(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    p, r, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f1}


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    ys, ps = [], []
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        pred = logits.argmax(dim=1)
        ys.extend(y.cpu().tolist())
        ps.extend(pred.cpu().tolist())
    return metrics(ys, ps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--feature", choices=["mfcc", "mel", "psd", "zcr"], default="mfcc")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--patience", type=int, default=8)
    ap.add_argument("--out", default="runs/fp32_baseline")
    args = ap.parse_args()

    seed_all(args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    ds = UAVAudioDataset(args.data_root, args.feature, AudioConfig())
    n_train = int(0.8 * len(ds))
    n_val = int(0.1 * len(ds))
    n_test = len(ds) - n_train - n_val
    train_ds, val_ds, test_ds = random_split(
        ds, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(args.seed)
    )

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size)
    test_loader = DataLoader(test_ds, batch_size=args.batch_size)

    input_length = ds[0][0].shape[-1]
    model = Shield1DFCNN(input_length, ModelConfig()).to(device)
    print(f"input_length={input_length}, flatten_dim={model.flatten_dim}")

    criterion = nn.CrossEntropyLoss()
    optim = torch.optim.Adam(model.parameters(), lr=args.lr)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    best = -1.0
    bad = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        for x, y, _ in train_loader:
            x, y = x.to(device), y.to(device)
            optim.zero_grad(set_to_none=True)
            loss = criterion(model(x), y)
            loss.backward()
            optim.step()

        val = evaluate(model, val_loader, device)
        print(f"epoch={epoch:03d} val={val}")

        if val["accuracy"] > best:
            best = val["accuracy"]
            bad = 0
            torch.save(
                {
                    "model": model.state_dict(),
                    "model_cfg": model.cfg.__dict__,
                    "input_length": input_length,
                    "feature": args.feature,
                    "val": val,
                },
                out / "best.pt"
            )
        else:
            bad += 1
            if bad >= args.patience:
                print("Early stopping.")
                break

    ckpt = torch.load(out / "best.pt", map_location=device)
    model.load_state_dict(ckpt["model"])
    test = evaluate(model, test_loader, device)

    result = {
        "feature": args.feature,
        "input_length": input_length,
        "flatten_dim": model.flatten_dim,
        "test": test,
        "source_target_fp32_accuracy": 0.8991,
    }
    (out / "metrics.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
