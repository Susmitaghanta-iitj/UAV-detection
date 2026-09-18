from __future__ import annotations
import argparse,json,csv
from pathlib import Path
from .targets import TARGETS
from .collect_static import collect
from .compare_targets import compare

def load_json_if(path):
    if not path: return {}
    p=Path(path)
    return json.loads(p.read_text()) if p.exists() else {}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--precision-results",default=None,
                    help="precision-matrix JSON, if available")
    ap.add_argument("--fpga-results",default=None,
                    help="Optional JSON with fpga_power/fpga_latency")
    ap.add_argument("--asic-results",default=None,
                    help="Optional JSON with asic_freq/asic_area/asic_power")
    ap.add_argument("--outdir",default="reproduction_results")
    args=ap.parse_args()

    outdir=Path(args.outdir);outdir.mkdir(parents=True,exist_ok=True)

    reproduced=collect()

    p=load_json_if(args.precision_results)
    # Accept either baseline/reduced matrix structure or flat dict
    if p:
        src=p.get("reduced_8704",p.get("baseline_35072",p))
        precis=src.get("precisions",{})
        if "fp32" in precis: reproduced["fp32_accuracy"]=100*precis["fp32"]["accuracy"]
        if "int8" in precis: reproduced["int8_accuracy"]=100*precis["int8"]["accuracy"]
        if "fxp8_q34" in precis: reproduced["fxp8_accuracy"]=100*precis["fxp8_q34"]["accuracy"]

    reproduced.update(load_json_if(args.fpga_results))
    reproduced.update(load_json_if(args.asic_results))

    rows=compare(TARGETS,reproduced)

    (outdir/"reproduced_metrics.json").write_text(json.dumps(reproduced,indent=2))
    (outdir/"comparison.json").write_text(json.dumps(rows,indent=2))

    with (outdir/"comparison.csv").open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=rows[0].keys())
        wr.writeheader();wr.writerows(rows)

    # Markdown report
    md=["# SHIELD/AHCO Reproduction Status","","| Metric | Reported | Reproduced | Unit | Status |",
        "|---|---:|---:|---|---|"]
    for r in rows:
        md.append(f"| {r['metric']} | {r['reported']} | {r['reproduced']} | {r['unit']} | {r['status']} |")
    md += ["","## Notes",
           "- `pending` means the repository does not yet have measured data for that metric.",
           "- Accuracy requires a trained checkpoint + dataset.",
           "- FPGA/ASIC PPA must come from an actual tool flow; they are never fabricated.",
           "- Static shape/MAC values are derived directly from the reconstructed source-aligned architecture."]
    (outdir/"REPORT.md").write_text("\n".join(md))
    print((outdir/"REPORT.md").read_text())

if __name__=="__main__":main()
