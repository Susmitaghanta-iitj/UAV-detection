from __future__ import annotations
import copy
from torch import nn
from .qat_layers import QATConv1d,QATLinear


def apply_bit_assignment(model: nn.Module, assignment: dict[str,int]) -> nn.Module:
    m=copy.deepcopy(model)

    def recurse(parent,prefix=""):
        for name,child in list(parent.named_children()):
            full=f"{prefix}.{name}" if prefix else name
            if isinstance(child,nn.Conv1d) and full in assignment:
                setattr(parent,name,QATConv1d(child,assignment[full]))
            elif isinstance(child,nn.Linear) and full in assignment:
                setattr(parent,name,QATLinear(child,assignment[full]))
            else:
                recurse(child,full)
    recurse(m)
    return m
