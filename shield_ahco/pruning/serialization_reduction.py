from __future__ import annotations
import torch
from torch import nn


class SerializationReducer(nn.Module):
    """
    Source-aligned transform reproducing the stated 35,072 -> 8,704
    flatten reduction.

    The thesis says structured channel pruning and depicts an additional
    pooling stage. Because the published figure/text are inconsistent,
    the default uses pool=4, the only value that reproduces 8,704 from
    256 x 137 exactly.
    """
    def __init__(self, pool: int = 4):
        super().__init__()
        self.pool = nn.MaxPool1d(pool, stride=pool)

    def forward(self, x):
        return self.pool(x)
