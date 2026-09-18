from __future__ import annotations
from dataclasses import dataclass

from shield_ahco.complete_layer.complete_layer_reference import (
    LayerQuantMeta, conv1d_complete
)

@dataclass
class PingPongMemory:
    a: list[int]
    b: list[int]
    src_is_a: bool = True

    @property
    def src(self):
        return self.a if self.src_is_a else self.b

    @property
    def dst(self):
        return self.b if self.src_is_a else self.a

    def swap(self):
        self.src_is_a = not self.src_is_a


def maxpool_codes(flat_codes, channels: int, length: int, pool: int):
    out_len = length // pool
    out = [0] * (channels*out_len)
    for c in range(channels):
        for ox in range(out_len):
            vals = [
                flat_codes[c*length + ox*pool + k]
                for k in range(pool)
            ]
            out[c*out_len + ox] = max(vals)
    return out


def flatten_ch_first(matrix):
    return [v for row in matrix for v in row]


def reshape_ch_first(flat, channels, length):
    return [flat[c*length:(c+1)*length] for c in range(channels)]


def conv_pool_block(
    input_codes,
    weight_codes,
    meta: LayerQuantMeta,
    cin: int,
    cout: int,
    length: int,
    kernel: int,
    pool: int,
    stride: int = 1,
    padding: int = 0,
):
    x = reshape_ch_first(input_codes, cin, length)
    conv = conv1d_complete(
        x, weight_codes, meta, stride=stride, padding=padding
    )
    conv_flat = flatten_ch_first(conv)
    conv_len = len(conv[0])
    pooled = maxpool_codes(conv_flat, cout, conv_len, pool)
    return conv_flat, pooled, conv_len, conv_len // pool
