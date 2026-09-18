from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import torch
from torch import nn

from shield_ahco.qat.qat_layers import QATConv1d, QATLinear


@dataclass
class TensorQuantMeta:
    bits: int
    low: float
    high: float
    scale: float
    levels: int
    shape: list[int]


def quantize_affine_to_codes(t: torch.Tensor, low: float, high: float, bits: int):
    levels = (1 << bits) - 1
    tc = torch.clamp(t.detach().cpu(), low, high)
    q = torch.round((tc - low) * levels / (high - low)).to(torch.int64)
    q = torch.clamp(q, 0, levels)
    scale = (high - low) / levels
    return q, scale


def export_module(module: nn.Module, outdir: Path, prefix: str):
    if not isinstance(module, (QATConv1d, QATLinear)):
        raise TypeError(type(module))

    bits = module.wq.bits
    low = float(torch.minimum(module.wq.low, module.wq.high - 1e-6).detach().cpu())
    high = float(torch.maximum(module.wq.high, module.wq.low + 1e-6).detach().cpu())

    qweight, scale = quantize_affine_to_codes(module.weight, low, high, bits)
    torch.save(qweight, outdir / f"{prefix}_weight_codes.pt")

    if module.bias is not None:
        torch.save(module.bias.detach().cpu(), outdir / f"{prefix}_bias_fp32.pt")

    alpha = float(module.aq.alpha.detach().cpu())

    meta = {
        "kind": module.__class__.__name__,
        "weight": asdict(TensorQuantMeta(
            bits=bits,
            low=low,
            high=high,
            scale=scale,
            levels=(1 << bits)-1,
            shape=list(module.weight.shape),
        )),
        "activation": {
            "bits": module.aq.bits,
            "alpha": alpha,
            "levels": (1 << module.aq.bits)-1,
            "scale": alpha / ((1 << module.aq.bits)-1),
        }
    }
    (outdir / f"{prefix}_meta.json").write_text(json.dumps(meta, indent=2))
    return meta


def export_qat_model(model: nn.Module, outdir: str | Path):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = {}

    for name, module in model.named_modules():
        if isinstance(module, (QATConv1d, QATLinear)):
            prefix = name.replace(".", "__")
            manifest[name] = export_module(module, outdir, prefix)

    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
