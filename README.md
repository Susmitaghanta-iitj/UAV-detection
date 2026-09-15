# AHCO-UAV: Precision-Aware Algorithm–Hardware Co-Design for Edge UAV Detection


## Overview

**AHCO-UAV** is an algorithm–hardware co-design framework for **resource-efficient UAV acoustic detection on edge-AI platforms**.

The project combines a lightweight acoustic deep-learning model with hardware-aware optimization techniques and a reusable FPGA/ASIC accelerator. The central idea is to avoid excessive hardware replication by using a **sequential, layer-reused compute architecture** with shared arithmetic resources.


## Key Contributions

- Lightweight **feature-driven 1D CNN (1D-F-CNN)** for UAV acoustic detection.
- Compact acoustic feature extraction using **MFCC**, with additional evaluation of Mel spectrogram, PSD, and ZCR representations.
- **Serialization-aware structured pruning** to reduce the flattened feature dimension from **35,072 to 8,704**.
- Approximately **75% reduction** in dense-layer serialization/computation overhead.
- Precision-aware quantization using **FP32, BF16, INT8, FXP8, HFP4, and Posit** numerical formats.
- **BOSE-8** layer-sensitivity-driven transprecision strategy for adaptive precision assignment.
- Reusable hardware primitives:
  - Multi-precision **MAC** unit
  - Configurable **activation-function** unit
  - Adaptive Approximate Dynamic (**AAD**) pooling unit
- **Sequential layer-reused accelerator** with a shared compute datapath.
- Memory reuse, serialization-aware scheduling, activation overlap, and efficient dataflow.
- **AXI-enabled accelerator IP** for FPGA integration.
- FPGA prototype on **PYNQ-Z2 / Zynq-7000**.
- ASIC synthesis and physical implementation targeting **40 nm CMOS**.

## System Architecture

The complete workflow can be viewed as four major stages:


        Acoustic UAV Data
               |
               v
      +-------------------+
      | Feature Extraction|
      | MFCC / Mel / PSD  |
      | / ZCR             |
      +-------------------+
               |
               v
      +-------------------+
      |   1D-F-CNN Model  |
      +-------------------+
               |
               v
      +-------------------+
      | Structured Pruning|
      | 35072 -> 8704     |
      +-------------------+
               |
               v
      +-------------------+
      | Precision-Aware   |
      | Quantization      |
      |     + BOSE-8      |
      +-------------------+
               |
               v
      +-------------------+
      | Sequential Layer- |
      | Reused Accelerator|
      +-------------------+
               |
          +----+----+
          |         |
          v         v
       FPGA       ASIC
      PYNQ-Z2     40 nm


## Algorithm-Level Design

The algorithmic pipeline is designed with hardware deployment constraints in mind.

### Acoustic Features

The project evaluates compact representations including:

- **MFCC — Mel-Frequency Cepstral Coefficients**
- Mel spectrogram
- Power Spectral Density (**PSD**)
- Zero Crossing Rate (**ZCR**)

MFCC provides the reported best trade-off between classification performance and computational cost.

### 1D-F-CNN

A lightweight feature-driven 1D convolutional neural network is used for UAV/non-UAV acoustic classification.

The model is intentionally designed to reduce computational complexity and memory requirements compared with heavier deep-learning architectures.

### Structured Pruning

A serialization-aware structured pruning method reduces the flattened feature vector:


Before pruning : 35,072 features
After pruning  :  8,704 features

Reduction      : ~75%


This directly reduces the amount of data that must pass through the sequential dense-layer hardware.

## Precision-Aware Computing

The framework investigates multiple numerical representations:

| Format | Main Objective |
|---|---|
| FP32 | High numerical precision |
| BF16 | Reduced precision with large dynamic range |
| INT8 | Low-cost integer computation |
| FXP8 | Lightweight fixed-point computation |
| Posit(8,2) | Tapered precision / dynamic range |
| Posit(4,1) | Ultra-low-bit computation |
| HFP4 | Aggressive low-bit computation |

### BOSE-8 Transprecision

The **BOSE-8** framework assigns numerical precision according to layer sensitivity rather than applying one uniform precision to the complete network.

This enables a trade-off between:

**Accuracy ↔ Hardware Cost ↔ Power ↔ Throughput**

## Hardware Architecture

The accelerator uses a **sequential layer-reused architecture**.

Instead of instantiating separate compute hardware for every neural-network layer, the same compute fabric is reused across layers.

### Main Hardware Blocks


                 +----------------------+
                 |     AXI Interface    |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   Control / FSM      |
                 | Layer Scheduling     |
                 +----------+-----------+
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
     +---------+      +-----------+     +-----------+
     | Weight/ |      | Multi-    |     | Activation|
     | Bias RAM|----->| Precision |---->| Function  |
     |         |      | MAC       |     | Unit      |
     +---------+      +-----------+     +-----------+
                            |
                            v
                    +---------------+
                    | Adaptive/AAD  |
                    | Pooling Unit  |
                    +-------+-------+
                            |
                            v
                       Output / RAM


### Design Principles

- Shared datapath reuse
- Sequential layer execution
- Multi-precision arithmetic
- Serialization-aware scheduling
- Memory reuse
- Activation overlap
- Pipeline and timing optimization
- AXI-based host integration

## FPGA Implementation

The accelerator was prototyped on the **PYNQ-Z2**, based on the Xilinx Zynq-7000 SoC.

The RTL implementation uses **Verilog HDL** and modular hardware blocks for:

- MAC computation
- Activation functions
- Pooling
- Runtime scheduling
- Memory interfacing
- AXI communication

### Reported FPGA Results

| Metric | Reported Result |
|---|---:|
| FPGA Platform | PYNQ-Z2 |
| Operating Frequency | ~100 MHz |
| FPGA Power | **0.94 W** |
| End-to-End Inference Latency | **116 ms** |
| LUTs | **3,924** |
| Registers / FFs | **2,452** |
| BRAM / DSP resources | **8** |

The comparative evaluation in the thesis reports the proposed architecture at **3.92K LUTs, 2.45K registers/FFs, 0.68 W, and 156 MHz** under its comparison setup. These values should be interpreted separately from the system-level FPGA result above.

## ASIC Implementation

The accelerator was evaluated using an ASIC flow targeting **40 nm CMOS**.

The reported flow includes:


RTL
 |
 v
Synthesis
 |
 v
Timing Optimization
 |
 v
Floorplanning
 |
 v
Clock Tree Synthesis
 |
 v
Placement
 |
 v
Routing
 |
 v
Power Analysis
 |
 v
Post-Layout Verification


### Reported ASIC Results

| Metric | Result |
|---|---:|
| Technology | 40 nm CMOS |
| Operating Frequency | **1.56 GHz** |
| Area | **3.29 mm²** |
| Power | **1.65 W** |

## Simulation

The RTL modules can be verified using a Verilog/SystemVerilog simulator.

Typical verification flow:


RTL Module
    |
    v
Testbench
    |
    v
Simulation
    |
    v
Waveform / Output Check
    |
    v
Functional Verification


Recommended practice is to keep an independent testbench for each reusable compute primitive before integrating the complete accelerator.

## Tools and Technologies

### Hardware / RTL

- Verilog HDL
- FPGA-based prototyping
- PYNQ-Z2 / Zynq-7000
- AXI interface
- BRAM / DSP / LUT-based implementation

### FPGA Design

- Xilinx Vivado
- RTL synthesis
- Implementation
- Timing analysis
- Power analysis
- IP integration

### ASIC

- Cadence digital implementation flow
- 40 nm CMOS target
- Synthesis
- Floorplanning
- CTS
- Placement and routing
- Post-layout analysis

### Machine Learning / Signal Processing

- UAV acoustic signals
- MFCC
- 1D CNN
- Structured pruning
- Quantization
- Mixed / transprecision arithmetic



The codes will be released post acceptance of the manuscript. 
