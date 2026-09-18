from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math

@dataclass(frozen=True)
class PositFormat:
    nbits: int
    es: int
    @property
    def nar(self): return 1 << (self.nbits-1)
    @property
    def mask(self): return (1 << self.nbits)-1

POSIT4_1 = PositFormat(4,1)
POSIT8_2 = PositFormat(8,2)

def decode_bits(ui, fmt):
    nbits, es, mask = fmt.nbits, fmt.es, fmt.mask
    ui &= mask
    if ui == 0: return 0.0
    if ui == fmt.nar: return float("nan")
    sign = (ui >> (nbits-1)) & 1
    if sign: ui = ((~ui)+1) & mask
    bitpos = nbits-2
    regime_bit = (ui >> bitpos) & 1
    run = 0
    while bitpos >= 0 and (((ui >> bitpos)&1) == regime_bit):
        run += 1
        bitpos -= 1
    k = run-1 if regime_bit else -run
    if bitpos >= 0: bitpos -= 1
    exp = 0
    for _ in range(es):
        exp <<= 1
        if bitpos >= 0:
            exp |= (ui >> bitpos) & 1
            bitpos -= 1
    frac, place = 1.0, 0.5
    while bitpos >= 0:
        if (ui >> bitpos) & 1: frac += place
        place *= 0.5
        bitpos -= 1
    value = (2.0 ** ((2 ** es)*k)) * (2.0 ** exp) * frac
    return -value if sign else value

@lru_cache(maxsize=None)
def codebook(nbits, es):
    fmt = PositFormat(nbits, es)
    pairs = []
    for c in range(1<<nbits):
        if c == fmt.nar: continue
        v = decode_bits(c, fmt)
        if math.isfinite(v): pairs.append((v,c))
    return tuple(sorted(pairs))

def encode_nearest(x, fmt):
    if math.isnan(x) or math.isinf(x): return fmt.nar
    cb = codebook(fmt.nbits, fmt.es)
    return min(cb, key=lambda vc: abs(x-vc[0]))[1]
