from __future__ import annotations
import math
from functools import lru_cache
import torch


def _ste(x: torch.Tensor, xq: torch.Tensor) -> torch.Tensor:
    """Straight-through estimator: quantized forward, identity backward."""
    return x + (xq - x).detach()


def fp32_fake_quant(x: torch.Tensor) -> torch.Tensor:
    return x.float()


def bf16_fake_quant(x: torch.Tensor, ste: bool = False) -> torch.Tensor:
    """
    BF16 emulation using PyTorch bfloat16 round-trip.
    Accumulation remains FP32 unless the caller explicitly requantizes accumulator state.
    """
    xq = x.to(torch.bfloat16).to(torch.float32)
    return _ste(x, xq) if ste else xq


def int8_symmetric_fake_quant(x: torch.Tensor, ste: bool = False, eps: float = 1e-12):
    """
    Per-tensor symmetric signed INT8 fake quantization.
    Returns dequantized tensor + scale.
    """
    amax = x.detach().abs().max()
    scale = torch.clamp(amax / 127.0, min=eps)
    q = torch.clamp(torch.round(x / scale), -127, 127)
    xq = q * scale
    return (_ste(x, xq) if ste else xq), scale


def fxp8_q34_fake_quant(x: torch.Tensor, ste: bool = False):
    """
    Signed FXP8 Q3.4:
      1 sign + 3 integer + 4 fractional bits.
    Range: [-8, 7.9375], step 1/16.
    This matches the thesis' Q3.4 description.
    """
    step = 2.0 ** -4
    xq = torch.clamp(torch.round(x / step) * step, -8.0, 7.9375)
    return _ste(x, xq) if ste else xq


def _decode_posit_bits(ui: int, nbits: int, es: int) -> float:
    """
    Decode an n-bit posit bit pattern to Python float.
    Uses standard posit rules: 0 => 0; 100..0 => NaR.
    """
    mask = (1 << nbits) - 1
    ui &= mask
    if ui == 0:
        return 0.0
    if ui == (1 << (nbits - 1)):
        return float("nan")

    sign = (ui >> (nbits - 1)) & 1
    if sign:
        ui = ((~ui) + 1) & mask  # posit two's-complement transform

    # Remove sign.
    payload = ui & ((1 << (nbits - 1)) - 1)
    bitpos = nbits - 2
    regime_bit = (payload >> bitpos) & 1

    run = 0
    while bitpos >= 0 and ((payload >> bitpos) & 1) == regime_bit:
        run += 1
        bitpos -= 1

    k = (run - 1) if regime_bit == 1 else -run

    # Skip terminating regime bit if present.
    if bitpos >= 0:
        bitpos -= 1

    exp = 0
    for _ in range(es):
        exp <<= 1
        if bitpos >= 0:
            exp |= (payload >> bitpos) & 1
            bitpos -= 1

    frac = 1.0
    fscale = 0.5
    while bitpos >= 0:
        if (payload >> bitpos) & 1:
            frac += fscale
        fscale *= 0.5
        bitpos -= 1

    useed = 2.0 ** (2 ** es)
    value = (useed ** k) * (2.0 ** exp) * frac
    return -value if sign else value


@lru_cache(maxsize=None)
def posit_codebook(nbits: int, es: int):
    vals = []
    codes = []
    nar = 1 << (nbits - 1)
    for code in range(1 << nbits):
        if code == nar:
            continue
        v = _decode_posit_bits(code, nbits, es)
        if math.isfinite(v):
            vals.append(v)
            codes.append(code)
    pairs = sorted(zip(vals, codes), key=lambda z: z[0])
    values = torch.tensor([p[0] for p in pairs], dtype=torch.float64)
    codes = torch.tensor([p[1] for p in pairs], dtype=torch.int64)
    return values, codes


def posit_fake_quant(x: torch.Tensor, nbits: int, es: int, ste: bool = False) -> torch.Tensor:
    """
    True small-posit numerical emulation by nearest representable posit value.

    This is intentionally more faithful than the illustrative linear clipping
    used in the XR-NPE Gaze-LLE posit4.py/posit8.py scripts.
    """
    cb, _ = posit_codebook(nbits, es)
    cb = cb.to(device=x.device, dtype=x.dtype)

    flat = x.reshape(-1)
    idx = torch.bucketize(flat, cb)

    lo_i = torch.clamp(idx - 1, 0, cb.numel() - 1)
    hi_i = torch.clamp(idx, 0, cb.numel() - 1)
    lo = cb[lo_i]
    hi = cb[hi_i]
    choose_hi = (flat - lo).abs() > (flat - hi).abs()
    q = torch.where(choose_hi, hi, lo).reshape_as(x)

    return _ste(x, q) if ste else q


def posit8_2_fake_quant(x: torch.Tensor, ste: bool = False) -> torch.Tensor:
    return posit_fake_quant(x, 8, 2, ste)


def posit4_1_fake_quant(x: torch.Tensor, ste: bool = False) -> torch.Tensor:
    return posit_fake_quant(x, 4, 1, ste)


@lru_cache(maxsize=None)
def minifloat_codebook(exp_bits: int, mant_bits: int):
    """
    Finite minifloat codebook with:
      - 1 sign bit
      - all exponent encodings used as finite exponents
      - explicit zero
      - no Inf/NaN/subnormal encodings

    This is chosen to match the thesis' HFP4 ranges:
      E2M1 max = 6
      E3M0 max = 16
    """
    bias = (1 << (exp_bits - 1)) - 1
    vals = {0.0}
    for sign in (-1.0, 1.0):
        for e in range(1 << exp_bits):
            exponent = e - bias
            for m in range(1 << mant_bits):
                frac = 1.0 + (m / float(1 << mant_bits) if mant_bits else 0.0)
                vals.add(sign * (2.0 ** exponent) * frac)
    return torch.tensor(sorted(vals), dtype=torch.float64)


def minifloat_fake_quant(x: torch.Tensor, exp_bits: int, mant_bits: int, ste: bool = False):
    cb = minifloat_codebook(exp_bits, mant_bits).to(device=x.device, dtype=x.dtype)
    flat = x.reshape(-1)
    idx = torch.bucketize(flat, cb)
    lo_i = torch.clamp(idx - 1, 0, cb.numel() - 1)
    hi_i = torch.clamp(idx, 0, cb.numel() - 1)
    lo, hi = cb[lo_i], cb[hi_i]
    q = torch.where((flat-lo).abs() > (flat-hi).abs(), hi, lo).reshape_as(x)
    return _ste(x, q) if ste else q


def hfp4_e2m1_fake_quant(x: torch.Tensor, ste: bool = False):
    return minifloat_fake_quant(x, 2, 1, ste)


def hfp4_e3m0_fake_quant(x: torch.Tensor, ste: bool = False):
    return minifloat_fake_quant(x, 3, 0, ste)


QUANTIZERS = {
    "fp32": fp32_fake_quant,
    "bf16": bf16_fake_quant,
    "int8": lambda x, ste=False: int8_symmetric_fake_quant(x, ste=ste)[0],
    "fxp8_q34": fxp8_q34_fake_quant,
    "posit8_2": posit8_2_fake_quant,
    "posit4_1": posit4_1_fake_quant,
    "hfp4_e2m1": hfp4_e2m1_fake_quant,
    "hfp4_e3m0": hfp4_e3m0_fake_quant,
}
