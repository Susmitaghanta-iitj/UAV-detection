from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path

def run(cmd,allow=()):
    print("+"," ".join(map(str,cmd)))
    p=subprocess.run(cmd)
    if p.returncode not in (0,*allow): raise SystemExit(p.returncode)
    return p.returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-root",default=None)
    ap.add_argument("--baseline-checkpoint",default=None)
    ap.add_argument("--reduced-checkpoint",default=None)
    ap.add_argument("--outdir",default="reproduction_results")
    args=ap.parse_args()
    py=sys.executable
    Path(args.outdir).mkdir(parents=True,exist_ok=True)

    # Always available static reconstruction
    run([py,"-m","shield_ahco.ahco_top.architecture_report"])

    precision_json=None
    if args.data_root and args.baseline_checkpoint and args.reduced_checkpoint:
        precision_json=str(Path(args.outdir)/"precision_matrix.json")
        run([
            py,"-m","shield_ahco.experiments.run_precision_matrix",
            "--data-root",args.data_root,
            "--baseline-checkpoint",args.baseline_checkpoint,
            "--reduced-checkpoint",args.reduced_checkpoint,
            "--out",precision_json
        ])

    cmd=[py,"-m","shield_ahco.repro.run_reproduction","--outdir",args.outdir]
    if precision_json: cmd += ["--precision-results",precision_json]
    run(cmd)

if __name__=="__main__":main()
