from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from .posit import POSIT4_1, POSIT8_2, decode_bits as pdecode, encode_nearest as pencode
from .minifloat import HFP4_E2M1, HFP4_E3M0, decode_bits as mfdecode, encode_nearest as mfencode

class TPMode(IntEnum):
    HFP4_E2M1 = 0
    HFP4_E3M0 = 1
    POSIT4_1  = 2
    POSIT8_2  = 3

CANON_FRAC = 16
CANON_SCALE = 1 << CANON_FRAC

@dataclass(frozen=True)
class CanonicalValue:
    q16_16: int
    is_nar: bool = False

    @property
    def value(self) -> float:
        return self.q16_16 / CANON_SCALE

def _to_q16_16(x: float) -> int:
    q = int(round(x * CANON_SCALE))
    lo = -(1 << 31)
    hi = (1 << 31) - 1
    return min(hi, max(lo, q))

def decode_to_canonical(code: int, mode: TPMode) -> CanonicalValue:
    if mode == TPMode.HFP4_E2M1:
        return CanonicalValue(_to_q16_16(mfdecode(code & 0xF, HFP4_E2M1)))
    if mode == TPMode.HFP4_E3M0:
        return CanonicalValue(_to_q16_16(mfdecode(code & 0xF, HFP4_E3M0)))
    if mode == TPMode.POSIT4_1:
        v = pdecode(code & 0xF, POSIT4_1)
        return CanonicalValue(0, True) if v != v else CanonicalValue(_to_q16_16(v))
    if mode == TPMode.POSIT8_2:
        v = pdecode(code & 0xFF, POSIT8_2)
        return CanonicalValue(0, True) if v != v else CanonicalValue(_to_q16_16(v))
    raise ValueError(mode)

def encode_from_canonical(q16_16: int, mode: TPMode) -> int:
    x = q16_16 / CANON_SCALE
    if mode == TPMode.HFP4_E2M1:
        return mfencode(x, HFP4_E2M1)
    if mode == TPMode.HFP4_E3M0:
        return mfencode(x, HFP4_E3M0)
    if mode == TPMode.POSIT4_1:
        return pencode(x, POSIT4_1)
    if mode == TPMode.POSIT8_2:
        return pencode(x, POSIT8_2)
    raise ValueError(mode)

def mul_canonical(a: CanonicalValue, b: CanonicalValue) -> tuple[int, bool]:
    if a.is_nar or b.is_nar:
        return 0, True
    # Q16.16 x Q16.16 -> Q32.32 raw product
    return a.q16_16 * b.q16_16, False

def product_q32_32_to_q16_16(prod: int) -> int:
    # round-to-nearest, ties away from zero
    sh = CANON_FRAC
    add = 1 << (sh - 1)
    if prod < 0:
        return -(((-prod) + add) >> sh)
    return (prod + add) >> sh
