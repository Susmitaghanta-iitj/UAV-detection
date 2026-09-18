from __future__ import annotations
import torch
from torch import nn


def ste_round(x: torch.Tensor) -> torch.Tensor:
    return x + (torch.round(x) - x).detach()


class LearnedWeightQuantizer(nn.Module):
    """
    Clean-room implementation of the camera-ready paper's learned clipping idea.

    Source-supported structure:
      - learned lower/upper clipping bounds W_l, W_h
      - n-bit quantization
      - clipped affine mapping into 2^n discrete levels

    Because the PDF text extraction of Eq. (3) is typographically ambiguous,
    we implement Eq. (4)'s explicit affine mapping directly:
        W_clip = clip(W, W_l, W_h)
        q = round((W_clip - W_l) * (2^n - 1)/(W_h - W_l))
        W_hat = W_l + q * (W_h - W_l)/(2^n - 1)

    This preserves the paper's stated clipping-and-quantization semantics without
    inventing an unsupported scale(k) interpretation.
    """
    def __init__(self, bits: int, init_low: float = -1.0, init_high: float = 1.0):
        super().__init__()
        self.bits = bits
        self.low = nn.Parameter(torch.tensor(float(init_low)))
        self.high = nn.Parameter(torch.tensor(float(init_high)))

    def forward(self, w: torch.Tensor) -> torch.Tensor:
        lo = torch.minimum(self.low, self.high - 1e-6)
        hi = torch.maximum(self.high, self.low + 1e-6)
        wc = torch.clamp(w, lo, hi)
        levels = float((1 << self.bits) - 1)
        q = ste_round((wc - lo) * levels / (hi - lo))
        return lo + q * (hi - lo) / levels


class PACTActivation(nn.Module):
    """
    PACT activation from the paper:
        y = 0.5 * (|x| - |x-alpha| + alpha)
        x_q = round(y * (2^n-1)/alpha) * alpha/(2^n-1)

    alpha is learned and constrained positive by softplus.
    """
    def __init__(self, bits: int, init_alpha: float = 6.0):
        super().__init__()
        self.bits = bits
        # inverse-softplus-ish positive initialization
        self.alpha_raw = nn.Parameter(torch.tensor(float(init_alpha)))

    @property
    def alpha(self):
        return torch.nn.functional.softplus(self.alpha_raw) + 1e-6

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        a = self.alpha
        # exact source PACT form
        y = 0.5 * (torch.abs(x) - torch.abs(x - a) + a)
        levels = float((1 << self.bits) - 1)
        q = ste_round(y * levels / a)
        return q * a / levels


def init_bounds_from_tensor(t: torch.Tensor, percentile: float = 0.999):
    """
    Stable initialization only; not claimed to be in the paper.
    Uses symmetric quantile initialization, then learned bounds can adapt.
    """
    flat = t.detach().abs().flatten()
    if flat.numel() == 0:
        return -1.0, 1.0
    k = max(1, min(flat.numel(), int(percentile * flat.numel())))
    val = torch.kthvalue(flat, k).values.item()
    val = max(val, 1e-3)
    return -val, val
