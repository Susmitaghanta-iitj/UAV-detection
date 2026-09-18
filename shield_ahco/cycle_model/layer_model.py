from dataclasses import dataclass

@dataclass(frozen=True)
class Conv1DLayer:
    cin:int; cout:int; length:int; kernel:int; stride:int=1; padding:int=0
    @property
    def out_length(self): return ((self.length+2*self.padding-self.kernel)//self.stride)+1
    @property
    def macs(self): return self.out_length*self.cout*self.cin*self.kernel

@dataclass(frozen=True)
class DenseLayer:
    din:int; dout:int
    @property
    def macs(self): return self.din*self.dout

@dataclass
class LayerCycles:
    name:str; compute_cycles:int; read_cycles:int; write_cycles:int; total_cycles:int

class SharedMacCycleModel:
    def __init__(self,macs_per_cycle=1,mem_reads_per_cycle=1,mem_writes_per_cycle=1):
        self.macs_per_cycle=macs_per_cycle
        self.mem_reads_per_cycle=mem_reads_per_cycle
        self.mem_writes_per_cycle=mem_writes_per_cycle
    def dense_cycles(self,name,l):
        c=(l.macs+self.macs_per_cycle-1)//self.macs_per_cycle
        r=(2*l.macs+self.mem_reads_per_cycle-1)//self.mem_reads_per_cycle
        w=(l.dout+self.mem_writes_per_cycle-1)//self.mem_writes_per_cycle
        return LayerCycles(name,c,r,w,c+r+w)
    def conv1d_cycles(self,name,l):
        c=(l.macs+self.macs_per_cycle-1)//self.macs_per_cycle
        r=(2*l.macs+self.mem_reads_per_cycle-1)//self.mem_reads_per_cycle
        outputs=l.out_length*l.cout
        w=(outputs+self.mem_writes_per_cycle-1)//self.mem_writes_per_cycle
        return LayerCycles(name,c,r,w,c+r+w)

def dense_serialization_reduction(before=35072,after=8704):
    return {"before":before,"after":after,"reduction_fraction":1-after/before,
            "speedup_if_dense_only":before/after}
