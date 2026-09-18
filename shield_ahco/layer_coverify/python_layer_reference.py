from __future__ import annotations
import json
from pathlib import Path

def dense_reference(case_path):
    d=json.loads(Path(case_path).read_text())
    act=d["act"]; weight=d["weight"]
    out=[]
    sum_qa=sum(act)
    for o,row in enumerate(weight):
        out.append({
            "o":o,
            "sum_qaqw":sum(a*w for a,w in zip(act,row)),
            "sum_qa":sum_qa
        })
    return out

def conv_reference(case_path):
    d=json.loads(Path(case_path).read_text())
    x=d["input"]; w=d["weight"]
    cin=d["cin"]; cout=d["cout"]; length=d["length"]
    kernel=d["kernel"]; stride=d["stride"]; padding=d["padding"]
    out_len=((length+2*padding-kernel)//stride)+1
    out=[]
    for oc in range(cout):
        for ox in range(out_len):
            s0=s1=0
            for ic in range(cin):
                for k in range(kernel):
                    ix=ox*stride+k-padding
                    qa=x[ic][ix] if 0<=ix<length else 0
                    qw=w[oc][ic][k]
                    s0 += qa*qw
                    s1 += qa
            out.append({"oc":oc,"ox":ox,"sum_qaqw":s0,"sum_qa":s1})
    return out
