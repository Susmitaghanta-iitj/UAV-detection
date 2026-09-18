from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class Target:
    name:str
    reported:float|int|str|None
    unit:str
    source_note:str
    status:str="reported"

TARGETS = [
    Target("fp32_accuracy",89.91,"%","thesis/camera-ready reported MFCC baseline"),
    Target("int8_accuracy",89.14,"%","thesis/camera-ready reported MFCC INT8"),
    Target("fxp8_accuracy",88.97,"%","thesis/camera-ready reported MFCC FXP8"),
    Target("flatten_baseline",35072,"elements","thesis reported baseline flatten size"),
    Target("flatten_reduced",8704,"elements","thesis reported reduced flatten size"),
    Target("fpga_power",0.94,"W","thesis/SHIELD reported FPGA power"),
    Target("fpga_latency",116.0,"ms","thesis/SHIELD reported end-to-end latency"),
    Target("asic_freq",1.56,"GHz","thesis reported ASIC frequency"),
    Target("asic_area",3.29,"mm^2","thesis reported ASIC area"),
    Target("asic_power",1.65,"W","thesis reported ASIC power"),
]
