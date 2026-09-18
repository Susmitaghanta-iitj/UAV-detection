# AHCO configuration — source-derived AHCO accelerator configuration

This stage stops using arbitrary synthetic layer dimensions for the architectural schedule.

The configuration ROM now transcribes the thesis Fig. 3.2 interpretation used in source reconciliation:
1. Conv: 1 -> 16, length 35,280, kernel 64, pool 8
2. Conv: 16 -> 32, length 4,410, kernel 32, pool 8
3. Conv: 32 -> 64, length 551, kernel 16, pool 4
4. Conv: 64 -> 256, length 137, kernel 4
5. Dense: 8,704 -> 128
6. Dense: 128 -> 64
7. Dense: 64 -> 2

Important source distinction:
- 35,072 is reproduced directly by the thesis waveform architecture.
- 8,704 is the thesis' reported post-pruning/serialization dimension, but the figure's
  literal extra pool-8 label is inconsistent with that number. As documented since source reconciliation,
  the report-aligned path uses the dimensionally consistent reduction to 8,704.
- The camera-ready 512->256->128->64 feature-vector network remains a separate source profile.

The RTL here is a configuration ROM + global layer scheduler, not a claim that the thesis
used this exact register encoding.
