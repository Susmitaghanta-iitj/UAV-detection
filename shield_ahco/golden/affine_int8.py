from __future__ import annotations
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class AffineFormat:
    bits: int
    low: float
    high: float

    @property
    def levels(self):
        return (1 << self.bits) - 1

    @property
    def scale(self):
        return (self.high - self.low) / self.levels


def encode(x: float, fmt: AffineFormat) -> int:
    xc = min(fmt.high, max(fmt.low, float(x)))
    q = round((xc - fmt.low) / fmt.scale)
    return max(0, min(fmt.levels, int(q)))


def decode(q: int, fmt: AffineFormat) -> float:
    q = max(0, min(fmt.levels, int(q)))
    return fmt.low + q * fmt.scale


@dataclass(frozen=True)
class PACTFormat:
    bits: int
    alpha: float

    @property
    def levels(self):
        return (1 << self.bits) - 1

    @property
    def scale(self):
        return self.alpha / self.levels


def pact_encode(x: float, fmt: PACTFormat) -> int:
    y = min(fmt.alpha, max(0.0, float(x)))
    q = round(y / fmt.scale)
    return max(0, min(fmt.levels, int(q)))


def pact_decode(q: int, fmt: PACTFormat) -> float:
    q = max(0, min(fmt.levels, int(q)))
    return q * fmt.scale
