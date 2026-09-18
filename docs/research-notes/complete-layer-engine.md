# complete layer — complete quantized Dense/Conv1D layer engine

This stage combines:
- integer activation/weight traversal,
- sum(q_a*q_w),
- sum(q_a),
- affine learned-clipping correction,
- bias,
- PACT clipping,
- 8-bit output requantization.

The Dense and Conv1D engines now emit the final 8-bit output code, not only intermediate sums.

Python and RTL use the same fixed-point Q24 metadata convention introduced in final-output equivalence.

Current scope:
- one common activation scale and one common weight affine scale per layer;
- one bias value per output channel/neuron;
- 8-bit output code.

Still intentionally left for later:
- pooling integration,
- double-buffered feature SRAM,
- scheduler across several layers,
- AXI host interface,
- exact paper pipeline overlap and CORDIC activation scheduling.
