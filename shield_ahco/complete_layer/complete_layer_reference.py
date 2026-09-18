from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

from shield_ahco.final_equiv.fixedpoint_metadata import FixedMeta
from shield_ahco.final_equiv.finalize_reference import fixed_finalize


@dataclass(frozen=True)
class LayerQuantMeta:
    scale_aw_q: int
    scale_al_q: int
    bias_q: list[int]
    alpha_q: int
    out_scale_q: int
    frac_bits: int = 24


def dense_complete(
    act_codes: Sequence[int],
    weight_codes: Sequence[Sequence[int]],
    meta: LayerQuantMeta,
):
    din=len(act_codes)
    dout=len(weight_codes)
    out=[]

    sum_qa=sum(int(a) for a in act_codes)

    for o in range(dout):
        sum_qaqw=sum(int(act_codes[i])*int(weight_codes[o][i]) for i in range(din))
        fm=FixedMeta(
            frac_bits=meta.frac_bits,
            scale_aw_q=meta.scale_aw_q,
            scale_al_q=meta.scale_al_q,
            bias_q=int(meta.bias_q[o]),
            alpha_q=meta.alpha_q,
            out_scale_q=meta.out_scale_q,
        )
        out.append(fixed_finalize(sum_qaqw,sum_qa,fm,8).out_code)

    return out


def conv1d_complete(
    x_codes: Sequence[Sequence[int]],
    weight_codes,
    meta: LayerQuantMeta,
    stride: int = 1,
    padding: int = 0,
):
    cin=len(x_codes)
    length=len(x_codes[0])
    cout=len(weight_codes)
    kernel=len(weight_codes[0][0])
    out_len=((length+2*padding-kernel)//stride)+1

    out=[[0 for _ in range(out_len)] for _ in range(cout)]

    for oc in range(cout):
        for ox in range(out_len):
            sum_qaqw=0
            sum_qa=0
            for ic in range(cin):
                for k in range(kernel):
                    ix=ox*stride+k-padding
                    qa=int(x_codes[ic][ix]) if 0<=ix<length else 0
                    qw=int(weight_codes[oc][ic][k])
                    sum_qaqw += qa*qw
                    sum_qa += qa

            fm=FixedMeta(
                frac_bits=meta.frac_bits,
                scale_aw_q=meta.scale_aw_q,
                scale_al_q=meta.scale_al_q,
                bias_q=int(meta.bias_q[oc]),
                alpha_q=meta.alpha_q,
                out_scale_q=meta.out_scale_q,
            )
            out[oc][ox]=fixed_finalize(sum_qaqw,sum_qa,fm,8).out_code
    return out
