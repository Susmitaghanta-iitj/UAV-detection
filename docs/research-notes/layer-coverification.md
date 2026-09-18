# layer co-verification — full Dense / Conv1D integer-layer co-verification

This stage extends MAC co-verification from a raw MAC accumulator to reusable neural-network layers.

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

Next step after layer co-verification:
- include exported per-layer scale and bias metadata;
- verify final dequantized/quantized layer outputs;
- then connect pooling/ReLU and execute a whole network block.
