from __future__ import annotations
from dataclasses import dataclass
from .fixedpoint_metadata import FixedMeta, from_fixed

@dataclass
class FinalizeResult:
    preact_float: float
    pact_float: float
    out_code: int

def exact_finalize(sum_qaqw: int, sum_qa: int,
                   sa: float, sw: float, wlow: float,
                   bias: float, alpha: float, out_bits: int = 8) -> FinalizeResult:
    pre = sa*sw*sum_qaqw + sa*wlow*sum_qa + bias
    y = min(alpha, max(0.0, pre))
    levels = (1 << out_bits) - 1
    q = int(round(y * levels / alpha)) if alpha > 0 else 0
    q = max(0, min(levels, q))
    return FinalizeResult(pre, y, q)

def fixed_finalize(sum_qaqw: int, sum_qa: int,
                   meta: FixedMeta, out_bits: int = 8) -> FinalizeResult:
    """
    Integer/fixed-point mirror of RTL:
      term0 = sum_qaqw * scale_aw_q
      term1 = sum_qa   * scale_al_q
      pre_q = term0 + term1 + bias_q
    All scale constants are in Q(frac_bits).

    Output code is computed as round(y / out_scale).
    """
    pre_q = (
        int(sum_qaqw) * int(meta.scale_aw_q)
        + int(sum_qa) * int(meta.scale_al_q)
        + int(meta.bias_q)
    )
    # term products are still Q(frac_bits), because sums are integers.
    alpha_q = int(meta.alpha_q)
    y_q = min(alpha_q, max(0, pre_q))

    levels = (1 << out_bits) - 1
    if meta.out_scale_q <= 0:
        q = 0
    else:
        q = (y_q + meta.out_scale_q//2) // meta.out_scale_q
    q = max(0, min(levels, int(q)))

    return FinalizeResult(
        from_fixed(pre_q, meta.frac_bits),
        from_fixed(y_q, meta.frac_bits),
        q,
    )
