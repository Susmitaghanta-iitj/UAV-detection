from __future__ import annotations
import copy
import torch
from torch import nn
import torch.nn.functional as F
from .quantizers import QUANTIZERS


class FakeQuantConv1d(nn.Module):
    def __init__(self, src: nn.Conv1d, precision: str, quantize_activation: bool = True):
        super().__init__()
        self.precision = precision
        self.quantize_activation = quantize_activation
        self.stride = src.stride
        self.padding = src.padding
        self.dilation = src.dilation
        self.groups = src.groups
        self.weight = nn.Parameter(src.weight.detach().clone(), requires_grad=False)
        self.bias = None if src.bias is None else nn.Parameter(src.bias.detach().clone(), requires_grad=False)

    def forward(self, x):
        q = QUANTIZERS[self.precision]
        xq = q(x) if self.quantize_activation else x
        wq = q(self.weight)
        bq = None if self.bias is None else q(self.bias)
        # Mathematical low-precision operands, FP32 host accumulation for precision emulation.
        return F.conv1d(xq, wq, bq, self.stride, self.padding, self.dilation, self.groups)


class FakeQuantLinear(nn.Module):
    def __init__(self, src: nn.Linear, precision: str, quantize_activation: bool = True):
        super().__init__()
        self.precision = precision
        self.quantize_activation = quantize_activation
        self.weight = nn.Parameter(src.weight.detach().clone(), requires_grad=False)
        self.bias = None if src.bias is None else nn.Parameter(src.bias.detach().clone(), requires_grad=False)

    def forward(self, x):
        q = QUANTIZERS[self.precision]
        xq = q(x) if self.quantize_activation else x
        wq = q(self.weight)
        bq = None if self.bias is None else q(self.bias)
        return F.linear(xq, wq, bq)


def quantize_model(model: nn.Module, precision: str, quantize_activation: bool = True) -> nn.Module:
    """
    PTQ-style fake quantization of Conv1d and Linear operands.

    FP32 accumulation is kept at this stage so that format error is isolated.
    A later bit-accurate golden model will emulate accumulator width/rounding.
    """
    if precision not in QUANTIZERS:
        raise KeyError(f"Unknown precision {precision}. Choices: {list(QUANTIZERS)}")

    m = copy.deepcopy(model)
    _replace(m, precision, quantize_activation)
    return m


def _replace(module, precision, quantize_activation):
    for name, child in list(module.named_children()):
        if isinstance(child, nn.Conv1d):
            setattr(module, name, FakeQuantConv1d(child, precision, quantize_activation))
        elif isinstance(child, nn.Linear):
            setattr(module, name, FakeQuantLinear(child, precision, quantize_activation))
        else:
            _replace(child, precision, quantize_activation)
