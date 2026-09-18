from dataclasses import dataclass
from .fixed import FXP8_Q34, INT8, encode as fx_encode, mul_raw
from .posit import POSIT4_1, POSIT8_2, encode_nearest as pencode, decode_bits as pdecode
from .minifloat import HFP4_E2M1, HFP4_E3M0, encode_nearest as mfencode, decode_bits as mfdecode
from .quire import SaturatingAccumulator

@dataclass
class MACResult:
    decoded: float
    code: int|None
    accumulator_raw: int|None

def dot_fxp8_q34(xs, ws, acc_width=32):
    acc = SaturatingAccumulator(acc_width)
    for x,w in zip(xs,ws):
        acc.add(mul_raw(fx_encode(float(x),FXP8_Q34),fx_encode(float(w),FXP8_Q34),FXP8_Q34))
    return MACResult(acc.value/256.0,None,acc.value)

def dot_int8(xs, ws, acc_width=32):
    acc = SaturatingAccumulator(acc_width)
    for x,w in zip(xs,ws): acc.add(fx_encode(x,INT8)*fx_encode(w,INT8))
    return MACResult(float(acc.value),None,acc.value)

def dot_posit(xs, ws, fmt=POSIT4_1):
    s = 0.0
    for x,w in zip(xs,ws):
        s += pdecode(pencode(float(x),fmt),fmt)*pdecode(pencode(float(w),fmt),fmt)
    c = pencode(s,fmt)
    return MACResult(pdecode(c,fmt),c,None)

def dot_minifloat(xs, ws, fmt=HFP4_E2M1):
    s = 0.0
    for x,w in zip(xs,ws):
        s += mfdecode(mfencode(float(x),fmt),fmt)*mfdecode(mfencode(float(w),fmt),fmt)
    c = mfencode(s,fmt)
    return MACResult(mfdecode(c,fmt),c,None)
