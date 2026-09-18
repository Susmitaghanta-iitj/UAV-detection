from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def run(cmd, allow_codes=()):
    print("+"," ".join(map(str,cmd)))
    p=subprocess.run(cmd)
    if p.returncode not in (0,*allow_codes):
        raise SystemExit(p.returncode)
    return p.returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--work",default="vectors/mac_coverification")
    ap.add_argument("--sequences",type=int,default=128)
    ap.add_argument("--taps",type=int,default=32)
    args=ap.parse_args()

    py=sys.executable
    work=Path(args.work)
    run([py,"-m","shield_ahco.coverify.generate_accum_vectors",
         "--outdir",str(work),"--sequences",str(args.sequences),"--taps",str(args.taps)])
    run([py,"-m","shield_ahco.coverify.make_sv_input",
         "--json",str(work/"accum_sequences.json"),
         "--out",str(work/"accum_sequences_flat.txt")])

    rc=run([py,"-m","shield_ahco.coverify.run_sv_regression",
            "--repo",".","--work",str(work)], allow_codes=(2,))
    if rc==2:
        print("Regression vectors ready; RTL simulation skipped because simulator is not installed.")
        return

    run([py,"-m","shield_ahco.coverify.compare_rtl_log",
         "--expected",str(work/"accum_expected.csv"),
         "--rtl-log",str(work/"rtl_results.log")])

if __name__=="__main__":
    main()
