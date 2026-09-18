# Shared Transprecision MAC — shared transprecision

Modes:
- 00: HFP4 E2M1
- 01: HFP4 E3M0
- 10: Posit(4,1)
- 11: Posit(8,2)

Clean-room architecture:
format decoder -> common signed Q16.16 canonical operands ->
shared 32x32 multiplier -> wide Q32.32 accumulator ->
single final rounding -> format-specific encoder.

This mirrors the source's *shared datapath / runtime precision* philosophy, but it is
not claimed to reproduce the author's undocumented internal representation exactly.

Why Q16.16 internally?
- it exactly represents all values of the 4-bit formats here;
- it provides one common multiplication path;
- it gives a straightforward Python/RTL equivalence target;
- it keeps the implementation synthesizable and easy to verify.

The source discusses shared preprocessing/mantissa logic and quire accumulation, but
does not disclose enough bit-level detail to reconstruct its exact internal datapath.
