import json
from .source_config import SOURCE_CONV,BASELINE_FLATTEN,REDUCED_FLATTEN,DENSE_DIMS,validate

def main():
    validate()
    rows=[]
    total_conv=0
    for i,c in enumerate(SOURCE_CONV,1):
        total_conv+=c.macs
        rows.append({
            "layer":f"conv{i}","cin":c.cin,"cout":c.cout,"length":c.length,
            "kernel":c.kernel,"pool":c.pool,"pool_out_length":c.pool_out_length,
            "macs":c.macs
        })
    dense_base=BASELINE_FLATTEN*128+128*64+64*2
    dense_red=REDUCED_FLATTEN*128+128*64+64*2
    print(json.dumps({
        "conv":rows,
        "baseline_flatten":BASELINE_FLATTEN,
        "reduced_flatten":REDUCED_FLATTEN,
        "dense_dims":DENSE_DIMS,
        "total_conv_macs":total_conv,
        "baseline_dense_macs":dense_base,
        "reduced_dense_macs":dense_red,
    },indent=2))
if __name__=="__main__":main()
