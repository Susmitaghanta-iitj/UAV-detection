# precision matrix precision fidelity note

This stage applies the precision emulation quantizers to the source reconciliation/7 source-aligned thesis network.

Source-supported precision facts:
- SHIELD8-UAV camera-ready reports FP32, BF16, INT8, and FXP8 support.
- The thesis precision table also discusses Posit(8,2), Posit(4,1), HFP4 E2M1, and HFP4 E3M0.
- The camera-ready paper provides learned clipping/PACT equations for low-precision quantisation.
- The reported MFCC accuracies include approximately 89.91% FP32, 89.14% INT8, and 88.97% FXP8.

Clean-room aspects in this repository:
- current INT8 uses symmetric per-tensor fake quantization;
- current Posit/HFP implementations use representable-value codebooks;
- current model wrappers quantize Conv1d/Linear operands while BatchNorm remains FP32;
- accumulator behavior is still modeled separately in the bit-accurate arithmetic path;
- accuracy numbers produced by this repository must be measured from a trained checkpoint and dataset, not assumed equal to the paper.

Therefore the matrix is an experimental reproduction harness, not a claim that every quantizer is byte-identical to the authors' code.
