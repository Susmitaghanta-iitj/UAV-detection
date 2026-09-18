from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--work",default="vectors/final_output_equivalence")
    a=ap.parse_args()
    repo=Path(a.repo).resolve()
    work=Path(a.work).resolve()
    work.mkdir(parents=True,exist_ok=True)

    if not (shutil.which("iverilog") and shutil.which("vvp")):
        print("SKIP: Icarus Verilog not installed.")
        return 2

    rtl=repo/"shield_ahco"/"rtl"/"final_equiv"/"qat_affine_pact_finalize.sv"
    tb=repo/"shield_ahco"/"rtl"/"final_equiv"/"tb_qat_affine_pact_finalize.sv"
    simv=work/"finalizer.simv"

    subprocess.run(["iverilog","-g2012","-s","tb_qat_affine_pact_finalize",
                    "-o",str(simv),str(rtl),str(tb)],check=True,cwd=work)
    subprocess.run(["vvp",str(simv),
                    f"+IN={work/'final_vectors.txt'}",
                    f"+OUT={work/'final_rtl.log'}"],check=True,cwd=work)
    subprocess.run([sys.executable,"-m","shield_ahco.final_equiv.compare_final_log",
                    "--log",str(work/"final_rtl.log")],check=True,cwd=repo)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
