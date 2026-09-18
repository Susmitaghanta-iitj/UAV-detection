# cycle-accurate Conv1D-to-pool — cycle-accurate complete Conv1D -> MaxPool block

Added:
- latency-aware complete quantized Conv1D engine;
- one-cycle source/weight SRAM valid handshakes;
- affine correction + bias + PACT output;
- temporary synchronous Conv-output SRAM;
- latency-aware MaxPool;
- fully wired Conv -> SRAM -> Pool top;
- matching Python cycle model.

The block now has no intentionally disconnected `conv_done`/`pool_done` placeholders.

The Python model is validated. SystemVerilog simulation still requires Icarus/Verilator
on the user's machine because this environment does not provide a simulator.

Next step:
chain two such blocks with ping-pong feature SRAM and then instantiate source-derived
layer dimensions/configuration metadata.
