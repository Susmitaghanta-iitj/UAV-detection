from __future__ import annotations
import copy
from torch import nn
from shield_ahco.software.quantization.quant_layers import FakeQuantConv1d, FakeQuantLinear

def quantize_source_model(model: nn.Module, precision: str, quantize_activation: bool = True) -> nn.Module:
    if precision == "fp32":
        return copy.deepcopy(model)
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
