# QAT-to-RTL equivalence equivalence fidelity note

This stage connects QAT learned-clipping/PACT QAT to integer-domain hardware arithmetic.

Key source-derived fact:
- weights are clipped between learned W_l/W_h and quantized;
- activations are PACT-quantized.

Key algebraic consequence:
because weight quantization is affine, a direct unsigned code multiply requires an
offset-correction term. This repository explicitly implements that correction.

Not source-specified:
- bias quantization format;
- exact accumulator width;
- fixed-point width of exported scales;
- exact RTL pipeline staging.

Therefore:
- bias remains high precision in the software oracle;
- RTL exposes parameterized accumulator widths;
- fixed-point scale metadata is software-generated;
- pipeline timing is our clean-room implementation.

The goal is mathematical equivalence to the reconstructed QAT equations, not a claim
that this is the authors' private RTL.
