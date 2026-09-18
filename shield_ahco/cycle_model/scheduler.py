from dataclasses import dataclass
from enum import IntEnum
class Op(IntEnum):
    NOP=0; CONV1D=1; DENSE=2; RELU=3; MAXPOOL1D=4
@dataclass(frozen=True)
class LayerConfig:
    op:Op; mode:int; cin_or_din:int; cout_or_dout:int; length:int=0; kernel:int=1; stride:int=1; padding:int=0; do_relu:bool=True
