from __future__ import annotations
from shield_ahco.ahco_top.source_config import SOURCE_CONV,BASELINE_FLATTEN,REDUCED_FLATTEN,DENSE_DIMS

def collect():
    total_conv=sum(c.macs for c in SOURCE_CONV)
    dense_base=BASELINE_FLATTEN*128+128*64+64*2
    dense_red=REDUCED_FLATTEN*128+128*64+64*2
    return {
        "flatten_baseline":BASELINE_FLATTEN,
        "flatten_reduced":REDUCED_FLATTEN,
        "conv_macs":total_conv,
        "dense_macs_baseline":dense_base,
        "dense_macs_reduced":dense_red,
        "total_macs_baseline":total_conv+dense_base,
        "total_macs_reduced":total_conv+dense_red,
    }
