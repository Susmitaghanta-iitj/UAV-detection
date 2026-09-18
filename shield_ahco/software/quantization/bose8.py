from __future__ import annotations
import copy
from dataclasses import dataclass
import torch
from torch import nn
from .quantizers import QUANTIZERS
from .quant_layers import FakeQuantConv1d, FakeQuantLinear


@dataclass
class LayerSensitivity:
    name: str
    score: float
    numel: int
    low_precision: str


def _weight_modules(model):
    for name, m in model.named_modules():
        if isinstance(m, (nn.Conv1d, nn.Linear)):
            yield name, m


def collect_gradient_sensitivity(model, loader, device="cpu", max_batches=8, low_precision="posit4_1"):
    """
    Practical implementation of the source's layer-sensitivity idea.

    score_l = mean(|Q_low(w_l)-w_l|) * ||grad_l|| / n_l

    The exact BOSE-8 implementation code is not provided in the supplied thesis.
    This is therefore a clean-room implementation of the documented principle,
    not a claim of byte-for-byte reproduction.
    """
    q = QUANTIZERS[low_precision]
    model = copy.deepcopy(model).to(device).train()
    criterion = nn.CrossEntropyLoss()

    for p in model.parameters():
        if p.grad is not None:
            p.grad.zero_()

    seen = 0
    for x, y, _ in loader:
        x, y = x.to(device), y.to(device)
        loss = criterion(model(x), y)
        loss.backward()
        seen += 1
        if seen >= max_batches:
            break

    out = []
    for name, m in _weight_modules(model):
        w = m.weight
        if w.grad is None:
            continue
        err = (q(w.detach()) - w.detach()).abs().mean()
        gnorm = torch.linalg.vector_norm(w.grad.detach())
        score = (err * gnorm / max(w.numel(), 1)).item()
        out.append(LayerSensitivity(name, score, w.numel(), low_precision))
    return sorted(out, key=lambda z: z.score)


def make_bose8_assignment(sensitivities, low_fraction=0.5,
                          low_precision="posit4_1", high_precision="posit8_2"):
    """
    Least-sensitive layers -> low precision.
    Most-sensitive layers -> higher precision.
    """
    n_low = int(round(len(sensitivities) * low_fraction))
    assignment = {}
    for i, s in enumerate(sensitivities):
        assignment[s.name] = low_precision if i < n_low else high_precision
    return assignment


def apply_layer_assignment(model, assignment, quantize_activation=True):
    m = copy.deepcopy(model)

    def recurse(parent, prefix=""):
        for name, child in list(parent.named_children()):
            full = f"{prefix}.{name}" if prefix else name
            if isinstance(child, nn.Conv1d) and full in assignment:
                setattr(parent, name, FakeQuantConv1d(child, assignment[full], quantize_activation))
            elif isinstance(child, nn.Linear) and full in assignment:
                setattr(parent, name, FakeQuantLinear(child, assignment[full], quantize_activation))
            else:
                recurse(child, full)
    recurse(m)
    return m
