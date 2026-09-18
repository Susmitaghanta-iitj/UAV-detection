from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def run_tb(repo,work,top,files,plusargs):
    simv=work/f"{top}.simv"
    subprocess.run(["iverilog","-g2012","-s",top,"-o",str(simv),*map(str,files)],check=True,cwd=work)
    subprocess.run(["vvp",str(simv),*plusargs],check=True,cwd=work)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--work",default="vectors/complete_layer")
    a=ap.parse_args()
    repo=Path(a.repo).resolve(); work=Path(a.work).resolve(); work.mkdir(parents=True,exist_ok=True)

    if not (shutil.which("iverilog") and shutil.which("vvp")):
        print("SKIP: Icarus Verilog not installed.")
        return 2

    core=repo/"shield_ahco"/"rtl"/"equivalence"/"qat_affine_mac_core.sv"
    fin=repo/"shield_ahco"/"rtl"/"final_equiv"/"qat_affine_pact_finalize.sv"

    de=repo/"shield_ahco"/"rtl"/"complete_layer"/"dense_complete_engine.sv"
    dtb=repo/"shield_ahco"/"rtl"/"complete_layer"/"tb_dense_complete_engine.sv"
    ce=repo/"shield_ahco"/"rtl"/"complete_layer"/"conv1d_complete_engine.sv"
    ctb=repo/"shield_ahco"/"rtl"/"complete_layer"/"tb_conv1d_complete_engine.sv"

    run_tb(repo,work,"tb_dense_complete_engine",[core,fin,de,dtb],[
        f"+ACT={work/'dense_complete_act.mem'}",
        f"+WGT={work/'dense_complete_wgt.mem'}",
        f"+BIAS={work/'dense_complete_bias.mem'}",
        f"+EXP={work/'dense_complete_expected.mem'}",
        f"+OUT={work/'dense_complete_rtl.log'}",
    ])

    run_tb(repo,work,"tb_conv1d_complete_engine",[core,fin,ce,ctb],[
        f"+IN={work/'conv_complete_input.mem'}",
        f"+WGT={work/'conv_complete_wgt.mem'}",
        f"+BIAS={work/'conv_complete_bias.mem'}",
        f"+EXP={work/'conv_complete_expected.mem'}",
        f"+OUT={work/'conv_complete_rtl.log'}",
    ])

    subprocess.run([
        sys.executable,"-m","shield_ahco.complete_layer.compare_complete_logs",
        "--dense-log",str(work/"dense_complete_rtl.log"),
        "--conv-log",str(work/"conv_complete_rtl.log")
    ],check=True,cwd=repo)

    return 0

if __name__=="__main__":
    raise SystemExit(main())
