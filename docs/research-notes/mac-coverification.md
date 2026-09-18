# MAC co-verification: Python ↔ SystemVerilog co-verification

Purpose:
- generate deterministic integer activation/weight sequences;
- compute Python expected accumulator values;
- run the same sequences through `qat_affine_mac_core.sv`;
- compare `sum(q_a*q_w)` and `sum(q_a)` bit-for-bit.

Supported simulator flow:
1. Icarus Verilog (`iverilog` + `vvp`)
2. Verilator (`verilator --binary --timing`)

Run:
```bash
python -m shield_ahco.coverify.run_all
```

A simulator is intentionally not bundled. If neither Icarus nor Verilator is installed,
the script exits with a clear SKIP status after generating all vectors and the testbench.

This stage verifies the integer accumulator core only. The next checkpoint is to include
the affine finalization/scaling block and then whole Conv1D/Dense layer transactions.
