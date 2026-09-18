# bit-accurate arithmetic RTL checkpoint

Implemented now:
- FXP8 Q3.4 multiply-accumulate with wide Q6.8 accumulator.
- exact Posit(4,1) decoder.
- Posit(4,1) decoded-product wide accumulator.

Still pending:
- final Posit output encoder/rounder,
- Posit(8,2) RTL,
- HFP4 E2M1/E3M0 RTL,
- shared runtime-selectable multiplier,
- exact quire width,
- activation/CORDIC,
- scheduler/memory/AXI.

The source describes quire-style accumulation but does not disclose the exact internal
quire width/encoding. This checkpoint therefore exposes the wide accumulator rather than
inventing undocumented details.
