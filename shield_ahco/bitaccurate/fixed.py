from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FixedFormat:
    total_bits: int
    frac_bits: int
    signed: bool = True
    @property
    def min_int(self): return -(1 << (self.total_bits-1)) if self.signed else 0
    @property
    def max_int(self): return (1 << (self.total_bits-1))-1 if self.signed else (1<<self.total_bits)-1
    @property
    def scale(self): return 1 << self.frac_bits

FXP8_Q34 = FixedFormat(8,4,True)
INT8 = FixedFormat(8,0,True)

def sat_int(v, fmt): return min(fmt.max_int, max(fmt.min_int, int(v)))

def encode(x, fmt, rounding="nearest"):
    y = x * fmt.scale
    q = int(round(y)) if rounding == "nearest" else int(y)
    return sat_int(q, fmt)

def decode(q, fmt): return sat_int(q, fmt) / fmt.scale
def mul_raw(a_q, b_q, fmt): return int(a_q) * int(b_q)
