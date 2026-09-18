from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache

@dataclass(frozen=True)
class MiniFloatFormat:
    exp_bits: int
    mant_bits: int
    @property
    def total_bits(self): return 1+self.exp_bits+self.mant_bits
    @property
    def bias(self): return (1 << (self.exp_bits-1))-1

HFP4_E2M1 = MiniFloatFormat(2,1)
HFP4_E3M0 = MiniFloatFormat(3,0)

def decode_bits(code, fmt):
    n = fmt.total_bits
    sign = (code >> (n-1)) & 1
    exp = (code >> fmt.mant_bits) & ((1<<fmt.exp_bits)-1)
    mant = code & ((1<<fmt.mant_bits)-1)
    if code & ((1<<(n-1))-1) == 0: return -0.0 if sign else 0.0
    frac = 1.0 + (mant/float(1<<fmt.mant_bits) if fmt.mant_bits else 0.0)
    v = (2.0 ** (exp-fmt.bias)) * frac
    return -v if sign else v

@lru_cache(maxsize=None)
def codebook(e,m):
    fmt = MiniFloatFormat(e,m)
    return tuple(sorted((decode_bits(c,fmt),c) for c in range(1<<fmt.total_bits)))

def encode_nearest(x, fmt):
    return min(codebook(fmt.exp_bits,fmt.mant_bits), key=lambda vc: abs(x-vc[0]))[1]
