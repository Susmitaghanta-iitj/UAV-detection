# source reconciliation source-reconciliation memo

The thesis and camera-ready paper describe different network variants.

## Thesis Fig. 3.2
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

## Fig. 3.3 inconsistency
The added post-pruning pool is visually labeled pool(8), but:
floor(137/8)×256 = 4,352.

The reported 8,704 value is:
floor(137/4)×256 = 8,704.

Both interpretations are preserved:
- claim-consistent default: extra pool 4 → 8,704
- literal figure mode: extra pool 8 → 4,352

## Camera-ready Fig. 2
A separate feature-driven variant is shown:
512→256→128→64 filters, kernel 3, pool 2,
dense 256→128→72→2, dropout 0.2/0.3.
It remains a separate architecture profile and is not silently merged with the thesis network.
