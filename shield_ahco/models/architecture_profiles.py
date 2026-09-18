from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class ConvStage:
    out_channels:int
    kernel_size:int
    pool_size:int|None

@dataclass(frozen=True)
class ArchitectureProfile:
    name:str
    input_kind:Literal["waveform","feature_vector"]
    input_length:int|None
    conv_stages:tuple[ConvStage,...]
    dense_dims:tuple[int,...]
    conv_dropout:float|None
    dense_dropout:float
    batch_norm:bool
    output_classes:int=2
    notes:str=""

THESIS_BASELINE=ArchitectureProfile(
    "thesis_fig3_2_waveform","waveform",35280,
    (ConvStage(16,64,8),ConvStage(32,32,8),ConvStage(64,16,4),ConvStage(256,4,None)),
    (128,64),None,0.25,True,2,
    "Thesis Fig.3.2; same-length convolution makes the reported 35,072 flatten dimension consistent."
)

ISVLSI_FEATURE=ArchitectureProfile(
    "isvlsi_fig2_feature","feature_vector",None,
    (ConvStage(512,3,2),ConvStage(256,3,2),ConvStage(128,3,2),ConvStage(64,3,2)),
    (256,128,72),0.2,0.3,False,2,
    "Camera-ready Fig.2; input M is not numerically specified."
)

def trace_profile(profile,input_length=None):
    L=input_length if input_length is not None else profile.input_length
    if L is None: raise ValueError("input_length required")
    c=1; trace=[{"op":"input","channels":1,"length":L,"elements":L}]
    for i,s in enumerate(profile.conv_stages,1):
        c=s.out_channels
        trace.append({"op":f"conv{i}","channels":c,"length":L,"kernel":s.kernel_size,"elements":c*L})
        if s.pool_size:
            L=L//s.pool_size
            trace.append({"op":f"pool{i}","channels":c,"length":L,"pool":s.pool_size,"elements":c*L})
    return trace,c*L

def pruning_consistency():
    tr,base=trace_profile(THESIS_BASELINE)
    c,L=tr[-1]["channels"],tr[-1]["length"]
    return {
        "baseline_channels":c,
        "baseline_length":L,
        "baseline_flatten":base,
        "figure3_3_literal_pool8_flatten":c*(L//8),
        "claim_consistent_pool4_flatten":c*(L//4),
        "reported_post_pruning_flatten":8704,
    }
