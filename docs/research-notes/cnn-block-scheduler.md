# CNN-block integration — CNN block + ping-pong memory + scheduler

This stage begins accelerator-level integration rather than adding another arithmetic primitive.

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
The complete Conv1D engine from complete layer currently assumes simple synchronous transaction
timing, while a realistic SRAM-backed top level needs explicit read latency and valid/ready
handshakes. CNN-block integration therefore does NOT pretend the full block top has been cycle-accurately
wired. The shell leaves `conv_done/pool_done` disconnected on purpose.

This is preferable to hiding a memory-timing bug behind zero-latency assumptions.

Next step:
- cycle-accurate memory: make SRAM read latency explicit, add valid handshakes to Conv1D/Pool,
  fully connect `cnn_block_top.sv`, and co-verify one complete Conv->Pool block.
