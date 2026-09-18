# pruning pruning fidelity note

Source-supported facts:
- the thesis states structured channel pruning is used;
- the flatten dimension changes from 35,072 to 8,704;
- the post-pruning architecture adds a pooling stage;
- the purpose is to reduce dense MACs, serialized cycles, memory traffic, and latency.

Not source-specified:
- exact channel-importance metric;
- exact per-layer pruning ratios;
- whether channels are physically removed before the extra pooling stage;
- exact fine-tuning schedule after pruning.

Therefore this repository separates:
1. a source-aligned serialization reduction that exactly reproduces 8,704 using the
   dimensionally consistent extra pool-4; and
2. an optional clean-room L1 structured channel-pruning implementation for research
   experiments.

The L1 criterion must not be cited as the author's original pruning algorithm.
