from __future__ import annotations
import copy
import torch
from torch import nn
import torch.nn.functional as F
from .paper_quantizers import LearnedWeightQuantizer, PACTActivation, init_bounds_from_tensor


class QATConv1d(nn.Module):
    def __init__(self, src: nn.Conv1d, bits: int):
        super().__init__()
        self.weight = nn.Parameter(src.weight.detach().clone())
        self.bias = None if src.bias is None else nn.Parameter(src.bias.detach().clone())
        self.stride = src.stride
        self.padding = src.padding
        self.dilation = src.dilation
        self.groups = src.groups

        lo, hi = init_bounds_from_tensor(src.weight)
        self.wq = LearnedWeightQuantizer(bits, lo, hi)
        self.aq = PACTActivation(bits)

    def forward(self, x):
        xq = self.aq(x)
        wq = self.wq(self.weight)
        return F.conv1d(xq, wq, self.bias, self.stride, self.padding, self.dilation, self.groups)


class QATLinear(nn.Module):
    def __init__(self, src: nn.Linear, bits: int):
        super().__init__()
        self.weight = nn.Parameter(src.weight.detach().clone())
        self.bias = None if src.bias is None else nn.Parameter(src.bias.detach().clone())
        lo, hi = init_bounds_from_tensor(src.weight)
        self.wq = LearnedWeightQuantizer(bits, lo, hi)
        self.aq = PACTActivation(bits)

    def forward(self, x):
        return F.linear(self.aq(x), self.wq(self.weight), self.bias)


def convert_to_qat(model: nn.Module, bits: int) -> nn.Module:
    m = copy.deepcopy(model)
    _convert(m, bits)
    return m


def _convert(parent: nn.Module, bits: int):
    for name, child in list(parent.named_children()):
        if isinstance(child, nn.Conv1d):
            setattr(parent, name, QATConv1d(child, bits))
        elif isinstance(child, nn.Linear):
            setattr(parent, name, QATLinear(child, bits))
        else:
            _convert(child, bits)
