# QAT-to-RTL equivalence RTL equivalence checkpoint

The paper-derived QAT uses an affine learned-clipping weight quantizer and PACT activations.

Because the weight quantizer has non-zero lower bound W_l:

    w = W_l + q_w * S_w

and PACT activations satisfy:

    a = q_a * S_a

the dot product becomes:

    sum(a*w)
    = S_a*S_w * sum(q_a*q_w)
      + S_a*W_l * sum(q_a)

So hardware requires two integer reductions:
1. `sum_qaqw`
2. `sum_qa`

`qat_affine_mac_core.sv` accumulates both.
`qat_affine_finalize.sv` applies fixed-point scale metadata exported from Python.

This stage intentionally does not quantize bias unless a source-supported bias rule is available.
Bias is retained as a higher-precision post-accumulation term.
