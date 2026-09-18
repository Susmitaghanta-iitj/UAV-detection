from __future__ import annotations
from dataclasses import dataclass
from .canonical import TPMode, decode_to_canonical, encode_from_canonical, mul_canonical, CANON_SCALE

@dataclass
class TPAccumulator:
    mode: TPMode
    acc_q32_32: int = 0
    nar_seen: bool = False

    def clear(self):
        self.acc_q32_32 = 0
        self.nar_seen = False

    def mac_codes(self, a_code: int, b_code: int):
        a = decode_to_canonical(a_code, self.mode)
        b = decode_to_canonical(b_code, self.mode)
        p, nar = mul_canonical(a, b)
        if nar:
            self.nar_seen = True
        else:
            self.acc_q32_32 += p

    def output_code(self) -> int:
        if self.nar_seen:
            if self.mode == TPMode.POSIT4_1:
                return 0x8
            if self.mode == TPMode.POSIT8_2:
                return 0x80
            return 0
        # Q32.32 accumulation -> Q16.16 with one final rounding.
        sh = 16
        add = 1 << (sh - 1)
        if self.acc_q32_32 < 0:
            q16 = -(((-self.acc_q32_32) + add) >> sh)
        else:
            q16 = (self.acc_q32_32 + add) >> sh
        return encode_from_canonical(q16, self.mode)

    def output_value(self) -> float:
        from .canonical import decode_to_canonical
        return decode_to_canonical(self.output_code(), self.mode).value


def dot_codes(a_codes, b_codes, mode: TPMode):
    acc = TPAccumulator(mode)
    for a, b in zip(a_codes, b_codes):
        acc.mac_codes(a, b)
    return acc.output_code(), acc.output_value(), acc.acc_q32_32, acc.nar_seen
