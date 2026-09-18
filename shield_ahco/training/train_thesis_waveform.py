from __future__ import annotations
import argparse, json, random
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader, random_split
import librosa

from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline


class WaveformUAVDataset(Dataset):
    """
    Expected:
      root/uav/*.wav
      root/non_uav/*.wav

    Source-aligned waveform path:
      mono, 44.1 kHz, fixed 0.8 s = 35,280 samples.
    """
    def __init__(self, root):
        self.items=[]
        root=Path(root)
        for cname,label in [("non_uav",0),("uav",1)]:
            for wav in sorted((root/cname).rglob("*.wav")):
                x,_=librosa.load(wav,sr=44100,mono=True)
                n=35280
                for s in range(0,len(x)-n+1,n):
                    seg=x[s:s+n].astype(np.float32)
                    peak=max(float(np.max(np.abs(seg))),1e-8)
                    seg=seg/peak
                    self.items.append((seg,label,str(wav)))
        if not self.items:
            raise RuntimeError("No 0.8 s WAV segments found.")

    def __len__(self): return len(self.items)

    def __getitem__(self,i):
        x,y,key=self.items[i]
        return torch.from_numpy(x).unsqueeze(0), torch.tensor(y,dtype=torch.long), key


def metrics(pred, target):
    pred=pred.cpu(); target=target.cpu()
    acc=(pred==target).float().mean().item()
    tp=((pred==1)&(target==1)).sum().item()
    fp=((pred==1)&(target==0)).sum().item()
    fn=((pred==0)&(target==1)).sum().item()
    p=tp/max(tp+fp,1); r=tp/max(tp+fn,1)
    f=2*p*r/max(p+r,1e-12)
    return {"accuracy":acc,"precision":p,"recall":r,"f1":f}


@torch.no_grad()
def evaluate(model,loader,device):
    model.eval(); ps=[]; ys=[]
    for x,y,_ in loader:
        x,y=x.to(device),y.to(device)
        ps.append(model(x).argmax(1)); ys.append(y)
    return metrics(torch.cat(ps),torch.cat(ys))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",required=True)
    ap.add_argument("--post-pruning",action="store_true")
    ap.add_argument("--literal-pool8",action="store_true")
    ap.add_argument("--epochs",type=int,default=50)
    ap.add_argument("--batch-size",type=int,default=16)
    ap.add_argument("--lr",type=float,default=1e-3)
    ap.add_argument("--seed",type=int,default=7)
    ap.add_argument("--out",default="runs/thesis_waveform")
    args=ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    device="cuda" if torch.cuda.is_available() else "cpu"

    ds=WaveformUAVDataset(args.data_root)
    ntr=int(.8*len(ds)); nv=int(.1*len(ds)); nt=len(ds)-ntr-nv
    tr,va,te=random_split(ds,[ntr,nv,nt],generator=torch.Generator().manual_seed(args.seed))
    tl=DataLoader(tr,batch_size=args.batch_size,shuffle=True)
    vl=DataLoader(va,batch_size=args.batch_size)
    tel=DataLoader(te,batch_size=args.batch_size)

    model=make_thesis_baseline(
        post_pruning=args.post_pruning,
        reconcile_pruning_claim=not args.literal_pool8
    ).to(device)

    opt=torch.optim.Adam(model.parameters(),lr=args.lr)
    lossfn=nn.CrossEntropyLoss()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    best=-1

    for ep in range(1,args.epochs+1):
        model.train()
        for x,y,_ in tl:
            x,y=x.to(device),y.to(device)
            opt.zero_grad(set_to_none=True)
            loss=lossfn(model(x),y)
            loss.backward(); opt.step()
        val=evaluate(model,vl,device)
        print(ep,val)
        if val["accuracy"]>best:
            best=val["accuracy"]
            torch.save({
                "model":model.state_dict(),
                "post_pruning":args.post_pruning,
                "literal_pool8":args.literal_pool8,
                "flatten_dim":model.flatten_dim,
                "feature_shape":model.feature_shape,
                "val":val,
            },out/"best.pt")

    ck=torch.load(out/"best.pt",map_location=device)
    model.load_state_dict(ck["model"])
    test=evaluate(model,tel,device)
    result={"test":test,"flatten_dim":model.flatten_dim,"feature_shape":model.feature_shape}
    (out/"metrics.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
