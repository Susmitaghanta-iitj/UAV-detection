from __future__ import annotations
import json
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.pruning.structured_channel_pruning import count_conv_macs,dense_macs
from shield_ahco.experiments.precision_metadata import PRECISIONS, parameter_storage_bytes

def params(m): return sum(p.numel() for p in m.parameters())

def main():
    out={}
    for name,post in [("baseline_35072",False),("reduced_8704",True)]:
        m=make_thesis_baseline(post,True)
        pc=params(m); conv=count_conv_macs(m,35280); dense=dense_macs(m)
        out[name]={
            "flatten":m.flatten_dim,
            "params":pc,
            "conv_macs":conv,
            "dense_macs":dense,
            "total_macs":conv+dense,
            "storage_mb":{
                p:parameter_storage_bytes(pc,p)/(1024**2)
                for p in PRECISIONS
            }
        }
    out["reduction"]={
        "dense_macs":1-out["reduced_8704"]["dense_macs"]/out["baseline_35072"]["dense_macs"],
        "params":1-out["reduced_8704"]["params"]/out["baseline_35072"]["params"],
        "total_macs":1-out["reduced_8704"]["total_macs"]/out["baseline_35072"]["total_macs"],
    }
    print(json.dumps(out,indent=2))
if __name__=="__main__": main()
