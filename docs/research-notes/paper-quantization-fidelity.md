# QAT: paper-quantization fidelity

This stage specifically follows the camera-ready SHIELD8-UAV quantization equations.

Source-derived:
- layer-sensitivity ranking is based on the difference in quantization error between
  candidate precisions, weighted by the layer gradient norm and normalized by layer size;
- weights use learned clipping bounds W_l and W_h;
- activations use PACT with a learnable alpha;
- higher-sensitivity layers receive higher precision; less-sensitive layers use lower precision.

Implementation choice:
The PDF extraction of Eq. (3), scale(k), is typographically ambiguous.
Rather than inventing a malformed scale equation, this code implements the explicit
affine clipping/quantization mapping from Eq. (4) directly.

The current QAT path supports 4/8/16-bit learned-clipping arithmetic. It is intended
to reproduce the paper's INT8/FXP8-style training methodology first. Posit/HFP remain
handled by the separate representable-codebook path until the source provides a
Posit-specific learned-clipping training equation.

This stage should therefore be treated as a source-aligned QAT reconstruction,
not the authors' unreleased original code.
