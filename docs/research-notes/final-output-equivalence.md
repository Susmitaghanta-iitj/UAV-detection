# final-output equivalence — final output-code equivalence

layer co-verification verified layer traversal and the two integer reductions:
- sum(q_a*q_w)
- sum(q_a)

final-output equivalence adds:
- affine scale correction,
- bias,
- PACT clipping,
- final 8-bit output requantization.

The target equation is:

    preact =
      Sa*Sw*sum(q_a*q_w)
      + Sa*Wlow*sum(q_a)
      + bias

    y = clip(preact, 0, alpha)

    q_out = round(y / (alpha/255))

The software path includes:
- floating-point exact reference,
- fixed-point reference using Q24 constants.

The RTL path uses the same Q24 constants.

This is still a clean-room reconstruction:
the source does not disclose the exact fixed-point width used for scale metadata
or bias storage, so FRAC_W=24 is a verification choice, not an author-claimed detail.
