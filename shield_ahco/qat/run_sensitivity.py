from __future__ import annotations
import argparse,json
from pathlib import Path
import torch
from torch.utils.data import DataLoader,random_split

from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.training.train_thesis_waveform import WaveformUAVDataset
from shield_ahco.qat.layer_sensitivity import compute_layer_sensitivity,assign_precision


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",required=True)
    ap.add_argument("--checkpoint",required=True)
    ap.add_argument("--post-pruning",action="store_true")
    ap.add_argument("--high-bits",type=int,default=16)
    ap.add_argument("--low-bits",type=int,default=8)
    ap.add_argument("--high-fraction",type=float,default=.35)
    ap.add_argument("--batch-size",type=int,default=16)
    ap.add_argument("--out",default="runs/sensitivity.json")
    args=ap.parse_args()

    device="cuda" if torch.cuda.is_available() else "cpu"
    ds=WaveformUAVDataset(args.data_root)
    ntr=int(.8*len(ds));nv=int(.1*len(ds));nt=len(ds)-ntr-nv
    tr,_,_=random_split(ds,[ntr,nv,nt],generator=torch.Generator().manual_seed(7))
    loader=DataLoader(tr,batch_size=args.batch_size,shuffle=False)

    m=make_thesis_baseline(args.post_pruning,True)
    ck=torch.load(args.checkpoint,map_location="cpu")
    m.load_state_dict(ck["model"],strict=True)

    entries=compute_layer_sensitivity(m,loader,device,args.high_bits,args.low_bits)
    assignment=assign_precision(entries,args.high_fraction,
                                high_label=f"{args.high_bits}bit",
                                low_label=f"{args.low_bits}bit")
    payload={
        "entries":[e.__dict__ for e in entries],
        "assignment":assignment,
    }
    out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
