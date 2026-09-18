from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def find_simulator():
    if shutil.which("iverilog") and shutil.which("vvp"):
        return "iverilog"
    if shutil.which("verilator"):
        return "verilator"
    return None

def run_iverilog(repo: Path, work: Path):
    rtl = repo/"shield_ahco"/"rtl"/"equivalence"/"qat_affine_mac_core.sv"
    tb  = repo/"shield_ahco"/"rtl"/"coverify"/"tb_qat_affine_mac_core.sv"
    out = work/"simv"
    cmd=["iverilog","-g2012","-o",str(out),str(rtl),str(tb)]
    subprocess.run(cmd,check=True,cwd=work)
    subprocess.run(["vvp",str(out)],check=True,cwd=work)

def run_verilator(repo: Path, work: Path):
    rtl = repo/"shield_ahco"/"rtl"/"equivalence"/"qat_affine_mac_core.sv"
    tb  = repo/"shield_ahco"/"rtl"/"coverify"/"tb_qat_affine_mac_core.sv"
    cmd=[
        "verilator","--binary","--timing","-Wall",
        str(rtl),str(tb),"--top-module","tb_qat_affine_mac_core"
    ]
    subprocess.run(cmd,check=True,cwd=work)
    exe=work/"obj_dir"/"Vtb_qat_affine_mac_core"
    subprocess.run([str(exe)],check=True,cwd=work)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--work",default="vectors/mac_coverification")
    args=ap.parse_args()

    repo=Path(args.repo).resolve()
    work=Path(args.work).resolve()
    work.mkdir(parents=True,exist_ok=True)

    sim=find_simulator()
    if sim is None:
        print("SKIP: no supported SystemVerilog simulator found (iverilog/vvp or verilator).")
        print("Vectors and testbench were generated; run this command on a machine with either simulator installed.")
        return 2

    print("Using simulator:",sim)
    if sim=="iverilog":
        run_iverilog(repo,work)
    else:
        run_verilator(repo,work)

if __name__=="__main__":
    raise SystemExit(main())
