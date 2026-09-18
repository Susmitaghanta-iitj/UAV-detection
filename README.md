End-to-end software, quantization, bit-accurate modeling, synthesizable RTL, Python/SystemVerilog co-verification, cycle-accurate memory integration, and reproducibility tooling for the SHIELD/AHCO UAV acoustic-classification accelerator.

## Contents

- [Software baseline](#software-baseline)
- [Quantized precision emulation](#quantized-precision-emulation)
- [Bit-accurate arithmetic and first RTL](#bit-accurate-arithmetic-and-first-rtl)
- [Shared runtime-selectable transprecision MAC](#shared-runtime-selectable-transprecision-mac)
- [Reusable layer engine](#reusable-conv1d-dense-and-pool-layer-engine)
- [Source reconciliation](#source-reconciliation)
- [Pruning fidelity](#pruning-fidelity)
- [Precision fidelity](#precision-fidelity)
- [Paper-derived QAT](#paper-derived-qat)
- [QAT-to-RTL equivalence](#qat-to-rtl-equivalence)
- [Python/SystemVerilog co-verification](#pythonsystemverilog-co-verification)
- [Layer-level co-verification](#layer-level-co-verification)
- [Final output equivalence](#final-output-equivalence)
- [Complete quantized layer engine](#complete-quantized-layer-engine)
- [CNN block scheduler](#cnn-block-scheduler)
- [Cycle-accurate SRAM](#cycle-accurate-sram)
- [Cycle-accurate Conv1D-to-pool](#cycle-accurate-conv1d-to-pool)
- [Source-derived AHCO top](#source-derived-ahco-top)
- [Reproduction harness](#reproduction-harness)
- [Current fidelity boundary](#current-fidelity-boundary)
- [Project webpage](docs/index.html)
- [Code manifest](CODE_MANIFEST.md)

## Software baseline

Reproduce the software path:

raw WAV audio
→ 0.8 s segmentation
→ amplitude normalization
→ MFCC-20 / Mel / PSD / ZCR feature extraction
→ 1D-F-CNN
→ baseline FP32 evaluation
→ later: pruning and low-precision emulation.

The supplied sources explicitly support:
- mono WAV audio, 44.1 kHz, 16-bit acquisition
- UAV/non-UAV binary detection
- MFCC, Mel spectrogram, PSD, ZCR
- MFCC-20 as the preferred compact feature
- 0.8 s windows
- Adam + cross-entropy + early stopping
- a four-block 1D CNN with kernel size 3, ReLU, max-pooling, dropout
- dense stages ending in a binary classifier

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Dataset layout

```text
data/
├── uav/
│   ├── *.wav
└── non_uav/
    ├── *.wav
```

## Example

```bash
python -m shield_ahco.software.train \
  --data-root data \
  --feature mfcc \
  --epochs 50
```

## Next milestones

1. Confirm FP32 training/evaluation baseline.
2. Match the reported flatten dimension.
3. Implement serialization-aware structured pruning.
4. Add INT8 / FXP8 iso-functional arithmetic emulation.
5. Implement BOSE-8 layer sensitivity.
6. Freeze a Python golden model for RTL verification.

## Quantized precision emulation

the precision-emulation flow adds PTQ/fake-quantized inference for:

- FP32
- BF16
- INT8 (symmetric per-tensor)
- FXP8 Q3.4
- Posit(8,2)
- Posit(4,1)
- HFP4 E2M1
- HFP4 E3M0
- BOSE-8-style layer-adaptive Posit(4,1)/Posit(8,2)

Run:

```bash
python -m shield_ahco.software.quantization.eval_precisions \
  --checkpoint runs/fp32_baseline/best.pt \
  --data-root data \
  --out runs/precision_sweep.json
```


## Bit-accurate arithmetic and first RTL

Added hardware-oriented arithmetic models for INT8, FXP8 Q3.4, Posit(4,1),
Posit(8,2), HFP4 E2M1, and HFP4 E3M0.

For fixed point, integer codes and accumulator fractional widths are explicit.
For Posit/HFP, operands are rounded to exact representable values and accumulated
with a single final rounding to model the source's quire-style intent without inventing
an undocumented quire width.

Generate vectors:
```bash
python -m shield_ahco.bitaccurate.generate_vectors --outdir vectors
```

First RTL:
- `shield_ahco/rtl/fxp8_q34_mac.sv`
- `shield_ahco/rtl/posit4_1_decode.sv`
- `shield_ahco/rtl/posit4_1_mac.sv`



## Shared runtime-selectable transprecision MAC

Added a complete clean-room shared datapath for:
- HFP4 E2M1
- HFP4 E3M0
- Posit(4,1)
- Posit(8,2)

The common internal representation is signed Q16.16. All formats decode into it,
share one multiplier and wide accumulator, then use one final rounding before
format-specific output encoding.

RTL:
- `hfp4_e2m1_decode.sv`
- `hfp4_e3m0_decode.sv`
- `posit4_1_decode_q16.sv`
- `posit8_2_decode.sv`
- `tp_decode.sv`
- `shared_tp_mac_core.sv`
- format encoders
- `tp_output_encode.sv`
- `shared_tp_mac_top.sv`



## Reusable Conv1D, Dense, and Pool layer engine
Adds Python layer execution and synthesizable RTL wrappers around the shared transprecision MAC.


Rendered figure:
- Input: 1×T waveform
- Conv1: 16 filters, kernel 64, BN+ReLU, MaxPool 8
- Conv2: 32 filters, kernel 32, BN+ReLU, MaxPool 8
- Conv3: 64 filters, kernel 16, BN+ReLU, MaxPool 4
- Conv4: 256 filters, kernel 4, BN+ReLU
- Flatten
- Dense 128 → Dense 64 → Dense 2 / sigmoid
- Dense dropout 0.25

Using 0.8 s at 44.1 kHz gives T=35,280. With same-length convolutions:
35,280 → /8 = 4,410 → /8 = 551 → /4 = 137
and 256×137 = 35,072 exactly.




This QAT flow specifically follows the camera-ready SHIELD8-UAV quantization equations.


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

This implementation should therefore be treated as a source-aligned QAT reconstruction,
not the authors' unreleased original code.

## QAT-to-RTL equivalence

This equivalence flow connects learned-clipping/PACT QAT to integer-domain hardware arithmetic.

Key fact:
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

## Python/SystemVerilog co-verification

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

This regression verifies the integer accumulator core only. The next checkpoint is to include
the affine finalization/scaling block and then whole Conv1D/Dense layer transactions.

## Layer-level co-verification

This layer-level flow extends MAC co-verification from a raw accumulator to reusable neural-network layers.

Dense verification:
- reads one activation vector;
- streams each output neuron's weight vector through the shared affine MAC core;
- emits `sum(q_a*q_w)` and `sum(q_a)` for every output neuron.

Conv1D verification:
- traverses output channel, output position, input channel, and kernel tap;
- explicitly inserts zero activation codes for padding;
- emits both integer reductions for every output element.

The current regression intentionally compares the pre-scale integer reductions.
This isolates address generation, loop ordering, padding behavior, and accumulation
from the separate fixed-point scaling/finalization block.

Next step after the layer-level co-verification flow:
- include exported per-layer scale and bias metadata;
- verify final dequantized/quantized layer outputs;
- then connect pooling/ReLU and execute a whole network block.

## Final output equivalence

the layer-level co-verification flow verified layer traversal and the two integer reductions:
- sum(q_a*q_w)
- sum(q_a)

the final-output equivalence flow adds:
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

## Complete quantized layer engine

This engine combines:
- integer activation/weight traversal,
- sum(q_a*q_w),
- sum(q_a),
- affine learned-clipping correction,
- bias,
- PACT clipping,
- 8-bit output requantization.

The Dense and Conv1D engines now emit the final 8-bit output code, not only intermediate sums.

Python and RTL use the same fixed-point Q24 metadata convention introduced in the final-output equivalence flow.

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

## CNN block scheduler

This work begins accelerator-level integration rather than adding another arithmetic primitive.

Implemented in Python:
- complete quantized Conv1D -> MaxPool block;
- two-block chain with output of block 1 feeding block 2;
- ping-pong feature-memory abstraction;
- simple cycle estimator;
- source-derived pooling-length checks:
  35,280 -> 4,410 -> 551 -> 137.

Implemented in RTL:
- ping-pong feature memory;
- 8-bit max-pool engine;
- Conv/Pool/memory-swap scheduler;
- CNN-block architectural shell.

Important limitation:
The complete Conv1D engine from the complete quantized layer engine currently assumes simple synchronous transaction
timing, while a realistic SRAM-backed top level needs explicit read latency and valid/ready
handshakes. the CNN-block integration therefore does NOT pretend the full block top has been cycle-accurately
wired. The shell leaves `conv_done/pool_done` disconnected on purpose.

This is preferable to hiding a memory-timing bug behind zero-latency assumptions.

Next step:
- the cycle-accurate SRAM integration: make SRAM read latency explicit, add valid handshakes to Conv1D/Pool,
  fully connect `cnn_block_top.sv`, and co-verify one complete Conv->Pool block.

## Cycle-accurate SRAM

the CNN-block integration deliberately left the accelerator shell incomplete because the earlier engines
implicitly assumed memory data was available immediately after presenting an address.

the cycle-accurate SRAM integration fixes that modeling problem.

Added:
- synchronous 8-bit SRAM with 1-cycle read latency and `rd_valid`;
- latency-aware Dense engine using ISSUE -> WAIT -> CONSUME;
- latency-aware MaxPool engine;
- scheduler with explicit start/run phases;
- an SRAM-backed Dense integration demo top;
- Python cycle model with the same latency convention.

**Cycle-accurate Conv1D-to-pool**

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

 AHCO configuration stops using arbitrary synthetic layer dimensions for the architectural schedule.

The configuration ROM now transcribes the thesis Fig. 3.2 interpretation used in the source-reconciliation analysis:
1. Conv: 1 -> 16, length 35,280, kernel 64, pool 8
2. Conv: 16 -> 32, length 4,410, kernel 32, pool 8
3. Conv: 32 -> 64, length 551, kernel 16, pool 4
4. Conv: 64 -> 256, length 137, kernel 4
5. Dense: 8,704 -> 128
6. Dense: 128 -> 64
7. Dense: 64 -> 2



The RTL here is a configuration ROM + global layer scheduler, not a claim that the thesis
used this exact register encoding.



Reported comparison targets currently tracked:
- FP32 accuracy 89.91%
- INT8 accuracy 89.14%
- FXP8 accuracy 88.97%
- flatten 35,072 -> 8,704
- FPGA power 0.94 W
- FPGA latency 116 ms
- ASIC 1.56 GHz / 3.29 mm^2 / 1.65 W


```bash
python -m shield_ahco.repro.pipeline \
  --data-root data \
  --baseline-checkpoint runs/thesis_waveform/best.pt \
  --reduced-checkpoint runs/thesis_waveform_reduced/best.pt \
  --outdir reproduction_results
```



## Repository map

- `shield_ahco/software/` — dataset, feature extraction, FP32 model, and training.
- `shield_ahco/software/quantization/` — precision emulation and BOSE-8 experiments.
- `shield_ahco/bitaccurate/` — fixed-point, minifloat, posit, quire, and transprecision arithmetic.
- `shield_ahco/qat/` — learned clipping, PACT, sensitivity analysis, and QAT.
- `shield_ahco/golden/` — integer golden models.
- `shield_ahco/rtl/` — synthesizable SystemVerilog and testbenches.
- `shield_ahco/*coverify*/` — Python/RTL vector generation and comparison.
- `shield_ahco/cycle_accurate_memory/` — explicit SRAM-latency and Dense cycle models.
- `shield_ahco/cycle_accurate_conv_pool/` — complete Conv1D-to-MaxPool cycle model.
- `shield_ahco/repro/` — end-to-end reproduction and gap reporting.
- [`CODE_MANIFEST.md`](CODE_MANIFEST.md) — complete tracked source-file inventory.
