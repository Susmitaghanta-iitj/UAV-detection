from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PrecisionSpec:
    name: str
    bits: int
    family: str

PRECISIONS = {
    "fp32": PrecisionSpec("fp32", 32, "float"),
    "bf16": PrecisionSpec("bf16", 16, "float"),
    "int8": PrecisionSpec("int8", 8, "integer"),
    "fxp8_q34": PrecisionSpec("fxp8_q34", 8, "fixed"),
    "posit8_2": PrecisionSpec("posit8_2", 8, "posit"),
    "posit4_1": PrecisionSpec("posit4_1", 4, "posit"),
    "hfp4_e2m1": PrecisionSpec("hfp4_e2m1", 4, "minifloat"),
    "hfp4_e3m0": PrecisionSpec("hfp4_e3m0", 4, "minifloat"),
}

def parameter_storage_bytes(param_count: int, precision: str) -> float:
    return param_count * PRECISIONS[precision].bits / 8.0

def compression_vs_fp32(precision: str) -> float:
    return 32.0 / PRECISIONS[precision].bits
