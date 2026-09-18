from __future__ import annotations
from dataclasses import dataclass
import copy
import torch
from torch import nn
from .paper_quantizers import LearnedWeightQuantizer, init_bounds_from_tensor


@dataclass
class SensitivityEntry:
    name: str
    score: float
    high_bits: int
    low_bits: int
    numel: int


def _quantize_detached(w: torch.Tensor, bits: int):
    lo, hi = init_bounds_from_tensor(w)
    levels = float((1 << bits) - 1)
    wc = torch.clamp(w.detach(), lo, hi)
    q = torch.round((wc - lo) * levels / (hi - lo))
    return lo + q * (hi - lo) / levels


def compute_layer_sensitivity(model: nn.Module, loader, device="cpu",
                              high_bits: int = 16, low_bits: int = 8,
                              max_batches: int = 8):
    """
    Source-aligned sensitivity structure from camera-ready Eq. (2):

      s_l = ( ||Q_high(w_l)-w_l|| - ||Q_low(w_l)-w_l|| )
            * ||grad L_wl|| / n_l

    The PDF notation includes indices s_c,k around candidate precisions.
    This implementation uses scalar mean absolute quantization errors for
    the two candidate precisions and multiplies their difference by
    gradient norm / layer size.
    """
    m = copy.deepcopy(model).to(device).train()
    lossfn = nn.CrossEntropyLoss()
    m.zero_grad(set_to_none=True)

    seen=0
    for x,y,_ in loader:
        x,y=x.to(device),y.to(device)
        loss=lossfn(m(x),y)
        loss.backward()
        seen += 1
        if seen >= max_batches:
            break

    out=[]
    for name,module in m.named_modules():
        if not isinstance(module,(nn.Conv1d,nn.Linear)):
            continue
        if module.weight.grad is None:
            continue

        w=module.weight.detach()
        qh=_quantize_detached(w,high_bits)
        ql=_quantize_detached(w,low_bits)
        eh=(qh-w).abs().mean()
        el=(ql-w).abs().mean()
        g=torch.linalg.vector_norm(module.weight.grad.detach())
        score=((el-eh).abs()*g/max(w.numel(),1)).item()

        out.append(SensitivityEntry(name,score,high_bits,low_bits,w.numel()))

    return sorted(out,key=lambda z:z.score, reverse=True)


def assign_precision(entries, high_fraction=0.35, high_label="bf16", low_label="int8"):
    n_high=max(1,int(round(len(entries)*high_fraction))) if entries else 0
    assignment={}
    for i,e in enumerate(entries):
        assignment[e.name]=high_label if i<n_high else low_label
    return assignment
