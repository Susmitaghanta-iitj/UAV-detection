from __future__ import annotations
import json
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.pruning.structured_channel_pruning import count_conv_macs, dense_macs

def params(m): return sum(p.numel() for p in m.parameters())

def main():
    baseline=make_thesis_baseline(False)
    reduced=make_thesis_baseline(True,True)
    literal=make_thesis_baseline(True,False)

    rows={}
    for name,m in [("baseline",baseline),("reported_8704",reduced),("literal_pool8",literal)]:
        rows[name]={
            "flatten":m.flatten_dim,
            "params":params(m),
            "conv_macs":count_conv_macs(m,35280),
            "dense_macs":dense_macs(m),
        }

    rows["dense_macs_reduction_vs_baseline"] = 1 - rows["reported_8704"]["dense_macs"]/rows["baseline"]["dense_macs"]
    print(json.dumps(rows,indent=2))

if __name__=="__main__":
    main()
