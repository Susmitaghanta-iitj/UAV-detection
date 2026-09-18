# cycle-accurate memory — explicit SRAM latency and valid handshakes

CNN-block integration deliberately left the accelerator shell incomplete because the earlier engines
implicitly assumed memory data was available immediately after presenting an address.

cycle-accurate memory fixes that modeling problem.

Added:
- synchronous 8-bit SRAM with 1-cycle read latency and `rd_valid`;
- latency-aware Dense engine using ISSUE -> WAIT -> CONSUME;
- latency-aware MaxPool engine;
- scheduler with explicit start/run phases;
- an SRAM-backed Dense integration demo top;
- Python cycle model with the same latency convention.

Important interpretation:
This is a clean-room cycle model. The source states on-chip feature memories, streamed
weights/features, shared datapath reuse, and FSM scheduling, but does not disclose the
exact BRAM/SRAM read latency or handshake implementation. One-cycle synchronous reads
are therefore our explicit verification assumption, not a claimed detail of the original RTL.

The next stage should apply the same valid/ready discipline to the complete Conv1D engine,
fully wire Conv -> temporary buffer -> MaxPool -> ping-pong destination memory, and verify
the complete block output under cycle-accurate memory timing.
