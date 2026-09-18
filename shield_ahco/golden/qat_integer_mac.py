from __future__ import annotations
from dataclasses import dataclass
from .affine_int8 import AffineFormat, PACTFormat, decode, pact_decode


@dataclass
class IntMacTrace:
    acc_code_domain: int
    output_float: float
    products: list[int]


def dot_affine_codes(
    act_codes,
    weight_codes,
    act_fmt: PACTFormat,
    weight_fmt: AffineFormat,
    bias: float = 0.0,
):
    """
    Exact integer-domain decomposition of:
      sum_i dequant(a_i) * dequant(w_i) + bias

    where:
      a_i = qa_i * Sa
      w_i = Wlow + qw_i * Sw

    This becomes:
      Sa*Sw*sum(qa*qw) + Sa*Wlow*sum(qa) + bias

    The first term is the pure integer MAC term. The second is an affine
    correction caused by the non-zero lower clipping bound.
    """
    assert len(act_codes) == len(weight_codes)

    sum_qa_qw = 0
    sum_qa = 0
    products = []
    for qa, qw in zip(act_codes, weight_codes):
        p = int(qa) * int(qw)
        products.append(p)
        sum_qa_qw += p
        sum_qa += int(qa)

    out = (
        act_fmt.scale * weight_fmt.scale * sum_qa_qw
        + act_fmt.scale * weight_fmt.low * sum_qa
        + float(bias)
    )
    return IntMacTrace(sum_qa_qw, out, products)
