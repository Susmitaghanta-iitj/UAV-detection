from __future__ import annotations
import argparse,json
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader, random_split

from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.training.train_thesis_waveform import WaveformUAVDataset,evaluate
from shield_ahco.qat.qat_layers import convert_to_qat


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",required=True)
    ap.add_argument("--fp32-checkpoint",required=True)
    ap.add_argument("--bits",type=int,choices=[4,8,16],default=8)
    ap.add_argument("--post-pruning",action="store_true")
    ap.add_argument("--epochs",type=int,default=15)
    ap.add_argument("--batch-size",type=int,default=16)
    ap.add_argument("--lr",type=float,default=1e-4)
    ap.add_argument("--seed",type=int,default=7)
    ap.add_argument("--out",default="runs/qat")
    args=ap.parse_args()

    device="cuda" if torch.cuda.is_available() else "cpu"
    ds=WaveformUAVDataset(args.data_root)
    ntr=int(.8*len(ds));nv=int(.1*len(ds));nt=len(ds)-ntr-nv
    tr,va,te=random_split(ds,[ntr,nv,nt],generator=torch.Generator().manual_seed(args.seed))
    tl=DataLoader(tr,batch_size=args.batch_size,shuffle=True)
    vl=DataLoader(va,batch_size=args.batch_size)
    tel=DataLoader(te,batch_size=args.batch_size)

    base=make_thesis_baseline(args.post_pruning,True)
    ck=torch.load(args.fp32_checkpoint,map_location="cpu")
    base.load_state_dict(ck["model"],strict=True)

    model=convert_to_qat(base,args.bits).to(device)
    opt=torch.optim.Adam(model.parameters(),lr=args.lr)
    lossfn=nn.CrossEntropyLoss()

    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    best=-1
    for ep in range(1,args.epochs+1):
        model.train()
        for x,y,_ in tl:
            x,y=x.to(device),y.to(device)
            opt.zero_grad(set_to_none=True)
            loss=lossfn(model(x),y)
            loss.backward();opt.step()
        val=evaluate(model,vl,device)
        print(ep,val)
        if val["accuracy"]>best:
            best=val["accuracy"]
            torch.save({
                "model":model.state_dict(),
                "bits":args.bits,
                "post_pruning":args.post_pruning,
                "val":val,
            },out/"best_qat.pt")

    qck=torch.load(out/"best_qat.pt",map_location=device)
    model.load_state_dict(qck["model"])
    test=evaluate(model,tel,device)
    (out/"metrics.json").write_text(json.dumps({"test":test,"bits":args.bits},indent=2))
    print(json.dumps({"test":test,"bits":args.bits},indent=2))

if __name__=="__main__":
    main()
