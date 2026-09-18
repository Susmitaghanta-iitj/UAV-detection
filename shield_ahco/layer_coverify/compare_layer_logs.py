from __future__ import annotations
import argparse, json
from pathlib import Path

def parse_dense(path):
    out={}
    for line in Path(path).read_text().splitlines():
        if not line.startswith("DENSE "): continue
        f=dict(x.split("=") for x in line.split()[1:])
        out[int(f["o"])] = (int(f["sum_qaqw"]),int(f["sum_qa"]))
    return out

def parse_conv(path):
    out={}
    for line in Path(path).read_text().splitlines():
        if not line.startswith("CONV "): continue
        f=dict(x.split("=") for x in line.split()[1:])
        out[(int(f["oc"]),int(f["ox"]))]=(int(f["sum_qaqw"]),int(f["sum_qa"]))
    return out

def check_dense(case,log):
    d=json.loads(Path(case).read_text())
    exp={e["o"]:(e["sum_qaqw"],e["sum_qa"]) for e in d["expected"]}
    got=parse_dense(log)
    mm=[(k,v,got.get(k)) for k,v in exp.items() if got.get(k)!=v]
    return len(exp),len(got),mm

def check_conv(case,log):
    d=json.loads(Path(case).read_text())
    exp={(e["oc"],e["ox"]):(e["sum_qaqw"],e["sum_qa"]) for e in d["expected"]}
    got=parse_conv(log)
    mm=[(k,v,got.get(k)) for k,v in exp.items() if got.get(k)!=v]
    return len(exp),len(got),mm

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dense-case")
    ap.add_argument("--dense-log")
    ap.add_argument("--conv-case")
    ap.add_argument("--conv-log")
    a=ap.parse_args()

    failed=False
    if a.dense_case and a.dense_log:
        n,g,mm=check_dense(a.dense_case,a.dense_log)
        print(f"dense expected={n} rtl={g} mismatches={len(mm)}")
        for x in mm[:20]: print("DENSE MISMATCH",x)
        failed |= bool(mm)
    if a.conv_case and a.conv_log:
        n,g,mm=check_conv(a.conv_case,a.conv_log)
        print(f"conv expected={n} rtl={g} mismatches={len(mm)}")
        for x in mm[:20]: print("CONV MISMATCH",x)
        failed |= bool(mm)
    raise SystemExit(1 if failed else 0)

if __name__=="__main__":
    main()
