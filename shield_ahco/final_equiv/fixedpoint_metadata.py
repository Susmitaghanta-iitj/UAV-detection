from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FixedMeta:
    frac_bits: int
    scale_aw_q: int
    scale_al_q: int
    bias_q: int
    alpha_q: int
    out_scale_q: int

def to_fixed(x: float, frac_bits: int) -> int:
    return int(round(float(x) * (1 << frac_bits)))

def from_fixed(q: int, frac_bits: int) -> float:
    return int(q) / float(1 << frac_bits)

def make_fixed_meta(sa: float, sw: float, wlow: float, bias: float,
                    alpha: float, out_bits: int = 8, frac_bits: int = 24) -> FixedMeta:
    """
    Export constants needed by RTL finalization.

    preact =
      Sa*Sw*sum_qaqw
      + Sa*Wlow*sum_qa
      + bias

    Then PACT:
      y = clip(preact, 0, alpha)
      qout = round(y / (alpha/(2^out_bits-1)))
    """
    scale_aw = sa * sw
    scale_al = sa * wlow
    out_scale = alpha / ((1 << out_bits) - 1)
    return FixedMeta(
        frac_bits=frac_bits,
        scale_aw_q=to_fixed(scale_aw, frac_bits),
        scale_al_q=to_fixed(scale_al, frac_bits),
        bias_q=to_fixed(bias, frac_bits),
        alpha_q=to_fixed(alpha, frac_bits),
        out_scale_q=to_fixed(out_scale, frac_bits),
    )
