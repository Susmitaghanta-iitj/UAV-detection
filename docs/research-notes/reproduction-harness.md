# reproduction harness — reproduction harness and gap report

This stage changes the project from "many building blocks" into a reproducibility workflow.

One command can now:
1. report the source-aligned architecture;
2. optionally run the precision experiment matrix when dataset/checkpoints are available;
3. ingest FPGA/ASIC result JSONs when real implementation data exists;
4. compare reproduced values against the source-reported targets;
5. emit JSON, CSV, and Markdown reports.

Crucially, missing PPA/accuracy results are marked `pending`.
The harness never fills them with guesses.

Reported comparison targets currently tracked:
- FP32 accuracy 89.91%
- INT8 accuracy 89.14%
- FXP8 accuracy 88.97%
- flatten 35,072 -> 8,704
- FPGA power 0.94 W
- FPGA latency 116 ms
- ASIC 1.56 GHz / 3.29 mm^2 / 1.65 W

These values are included as source-derived targets from the supplied thesis/paper,
not as reproduced measurements.

Example:
```bash
python -m shield_ahco.repro.pipeline \
  --data-root data \
  --baseline-checkpoint runs/thesis_waveform/best.pt \
  --reduced-checkpoint runs/thesis_waveform_reduced/best.pt \
  --outdir reproduction_results
```
