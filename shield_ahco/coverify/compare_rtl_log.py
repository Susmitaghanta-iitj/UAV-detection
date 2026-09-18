from __future__ import annotations
import argparse, csv
from pathlib import Path

def load_expected(csv_path):
    exp={}
    with open(csv_path,newline="") as f:
        for row in csv.DictReader(f):
            exp[int(row["seq"])] = (int(row["sum_qaqw"]), int(row["sum_qa"]))
    return exp

def load_rtl(log_path):
    got={}
    with open(log_path) as f:
        for line in f:
            line=line.strip()
            if not line.startswith("RESULT "):
                continue
            fields=dict(tok.split("=") for tok in line.split()[1:])
            got[int(fields["seq"])] = (int(fields["sum_qaqw"]), int(fields["sum_qa"]))
    return got

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--expected",default="vectors/mac_coverification/accum_expected.csv")
    ap.add_argument("--rtl-log",default="vectors/mac_coverification/rtl_results.log")
    args=ap.parse_args()

    exp=load_expected(args.expected)
    got=load_rtl(args.rtl_log)
    mismatches=[]
    for seq,val in exp.items():
        if got.get(seq) != val:
            mismatches.append((seq,val,got.get(seq)))
    print(f"expected={len(exp)} rtl={len(got)} mismatches={len(mismatches)}")
    for m in mismatches[:20]:
        print("MISMATCH",m)
    raise SystemExit(1 if mismatches else 0)

if __name__=="__main__":
    main()
