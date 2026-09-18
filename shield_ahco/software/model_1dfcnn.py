from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

import torch
from torch import nn


@dataclass(frozen=True)
class ModelConfig:
    conv_channels: tuple[int, ...] = (512, 256, 128, 64)
    kernel_size: int = 3
    pool_size: int = 2
    conv_dropout: float = 0.2
    dense_dims: tuple[int, ...] = (256, 128, 72)
    dense_dropout: float = 0.3
    num_classes: int = 2
    use_batchnorm: bool = False


class ConvBlock(nn.Module):
    def __init__(self, c_in, c_out, cfg: ModelConfig):
        super().__init__()
        pad = cfg.kernel_size // 2
        ops = [nn.Conv1d(c_in, c_out, cfg.kernel_size, padding=pad)]
        if cfg.use_batchnorm:
            ops.append(nn.BatchNorm1d(c_out))
        ops.extend([
            nn.ReLU(inplace=True),
            nn.MaxPool1d(cfg.pool_size),
            nn.Dropout(cfg.conv_dropout),
        ])
        self.block = nn.Sequential(*ops)

    def forward(self, x):
        return self.block(x)


class Shield1DFCNN(nn.Module):
    """
    Configurable clean-room reconstruction of the source 1D-F-CNN.

    Important: source figures/manuscripts are not fully consistent about every tensor
    dimension. Keep this model configurable until the reported flatten size is matched.
    """
    def __init__(self, input_length: int, cfg: ModelConfig | None = None):
        super().__init__()
        self.cfg = cfg or ModelConfig()

        blocks = []
        c = 1
        for out_c in self.cfg.conv_channels:
            blocks.append(ConvBlock(c, out_c, self.cfg))
            c = out_c
        self.features = nn.Sequential(*blocks)

        with torch.no_grad():
            dummy = torch.zeros(1, 1, input_length)
            z = self.features(dummy)
            flat_dim = int(z.numel())

        self.flatten_dim = flat_dim

        dense = []
        d = flat_dim
        for width in self.cfg.dense_dims:
            dense.extend([
                nn.Linear(d, width),
                nn.ReLU(inplace=True),
                nn.Dropout(self.cfg.dense_dropout),
            ])
            d = width
        dense.append(nn.Linear(d, self.cfg.num_classes))
        self.classifier = nn.Sequential(*dense)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1)
        return self.classifier(x)
