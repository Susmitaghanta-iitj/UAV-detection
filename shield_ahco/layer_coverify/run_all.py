from __future__ import annotations
import argparse, subprocess, sys

def run(cmd, allowed=()):
    print("+"," ".join(map(str,cmd)))
    p=subprocess.run(cmd)
    if p.returncode not in (0,*allowed):
        raise SystemExit(p.returncode)
    return p.returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--work",default="vectors/layer_coverification")
    args=ap.parse_args()
    py=sys.executable

    run([py,"-m","shield_ahco.layer_coverify.generate_dense_case","--outdir",args.work])
    run([py,"-m","shield_ahco.layer_coverify.generate_conv_case","--outdir",args.work])
    rc=run([py,"-m","shield_ahco.layer_coverify.run_layer_regression","--repo",".","--work",args.work],allowed=(2,3))
    if rc in (2,3):
        print("Layer vectors are ready; RTL simulation was not completed in this environment.")

if __name__=="__main__":
    main()
