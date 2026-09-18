from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def simulator():
    if shutil.which("iverilog") and shutil.which("vvp"): return "iverilog"
    if shutil.which("verilator"): return "verilator"
    return None

def run_iverilog(repo,work,top,tb,rtl_files,outlog,plusargs):
    simv=work/f"{top}.simv"
    cmd=["iverilog","-g2012","-s",top,"-o",str(simv)] + [str(x) for x in rtl_files] + [str(tb)]
    subprocess.run(cmd,check=True,cwd=work)
    subprocess.run(["vvp",str(simv),*plusargs],check=True,cwd=work)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--work",default="vectors/layer_coverification")
    args=ap.parse_args()

    repo=Path(args.repo).resolve()
    work=Path(args.work).resolve()
    work.mkdir(parents=True,exist_ok=True)
    sim=simulator()
    if not sim:
        print("SKIP: no Icarus/Verilator simulator installed.")
        return 2

    core=repo/"shield_ahco"/"rtl"/"equivalence"/"qat_affine_mac_core.sv"
    dense=repo/"shield_ahco"/"rtl"/"layer_coverify"/"dense_affine_engine.sv"
    dtb=repo/"shield_ahco"/"rtl"/"layer_coverify"/"tb_dense_affine_engine.sv"
    conv=repo/"shield_ahco"/"rtl"/"layer_coverify"/"conv1d_affine_engine.sv"
    ctb=repo/"shield_ahco"/"rtl"/"layer_coverify"/"tb_conv1d_affine_engine.sv"

    if sim=="iverilog":
        run_iverilog(repo,work,"tb_dense_affine_engine",dtb,[core,dense],work/"dense_rtl.log",[
            f"+ACT={work/'dense_act.mem'}",f"+WGT={work/'dense_weight.mem'}",f"+OUT={work/'dense_rtl.log'}"
        ])
        run_iverilog(repo,work,"tb_conv1d_affine_engine",ctb,[core,conv],work/"conv_rtl.log",[
            f"+IN={work/'conv_input.mem'}",f"+WGT={work/'conv_weight.mem'}",f"+OUT={work/'conv_rtl.log'}"
        ])
    else:
        print("Verilator layer runner not yet wired; use Icarus for layer co-verification.")
        return 3

    cmd=[
        sys.executable,"-m","shield_ahco.layer_coverify.compare_layer_logs",
        "--dense-case",str(work/"dense_case.json"),
        "--dense-log",str(work/"dense_rtl.log"),
        "--conv-case",str(work/"conv_case.json"),
        "--conv-log",str(work/"conv_rtl.log"),
    ]
    subprocess.run(cmd,check=True,cwd=repo)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
