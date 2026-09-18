from __future__ import annotations
import json
from pathlib import Path
import torch
import torch.nn.functional as F

from .affine_int8 import AffineFormat, PACTFormat, encode, decode, pact_encode, pact_decode
from .qat_integer_mac import dot_affine_codes


def load_exported_layer(export_dir: str | Path, layer_name: str):
    export_dir = Path(export_dir)
    prefix = layer_name.replace(".", "__")
    meta = json.loads((export_dir / f"{prefix}_meta.json").read_text())
    wq = torch.load(export_dir / f"{prefix}_weight_codes.pt", map_location="cpu")
    bias_path = export_dir / f"{prefix}_bias_fp32.pt"
    bias = torch.load(bias_path, map_location="cpu") if bias_path.exists() else None
    return meta, wq, bias


def dense_integer_golden(x_float, meta, w_codes, bias):
    wf = AffineFormat(**{
        "bits": meta["weight"]["bits"],
        "low": meta["weight"]["low"],
        "high": meta["weight"]["high"],
    })
    af = PACTFormat(
        bits=meta["activation"]["bits"],
        alpha=meta["activation"]["alpha"],
    )

    qa = [pact_encode(float(v), af) for v in x_float]
    out = []
    for o in range(w_codes.shape[0]):
        trace = dot_affine_codes(
            qa,
            [int(v) for v in w_codes[o].flatten()],
            af,
            wf,
            0.0 if bias is None else float(bias[o]),
        )
        out.append(trace.output_float)
    return torch.tensor(out, dtype=torch.float32), qa


def conv1d_integer_golden(x_float, meta, w_codes, bias, stride=1, padding=0):
    """
    x_float: [Cin, L]
    w_codes: [Cout, Cin, K]
    """
    wf = AffineFormat(
        bits=meta["weight"]["bits"],
        low=meta["weight"]["low"],
        high=meta["weight"]["high"],
    )
    af = PACTFormat(
        bits=meta["activation"]["bits"],
        alpha=meta["activation"]["alpha"],
    )

    cin, length = x_float.shape
    cout, _, k = w_codes.shape
    out_len = ((length + 2*padding - k)//stride)+1

    qx = [[pact_encode(float(x_float[c,i]), af) for i in range(length)] for c in range(cin)]
    out = torch.empty(cout, out_len)

    for oc in range(cout):
        for ox in range(out_len):
            acodes=[]
            wcodes=[]
            for ic in range(cin):
                for kk in range(k):
                    ix=ox*stride+kk-padding
                    acodes.append(qx[ic][ix] if 0 <= ix < length else 0)
                    wcodes.append(int(w_codes[oc,ic,kk]))
            tr = dot_affine_codes(
                acodes,wcodes,af,wf,
                0.0 if bias is None else float(bias[oc])
            )
            out[oc,ox]=tr.output_float
    return out, qx
