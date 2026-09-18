from dataclasses import dataclass

@dataclass(frozen=True)
class ConvCfg:
    cin:int; cout:int; length:int; kernel:int; pool:int|None
    @property
    def conv_out_length(self): return self.length
    @property
    def pool_out_length(self):
        return self.length if self.pool is None else self.length//self.pool
    @property
    def macs(self): return self.cout*self.length*self.cin*self.kernel

# Thesis Fig. 3.2 transcription under the same-length-convolution
# interpretation that exactly reproduces the reported 35,072 flatten size.
SOURCE_CONV = (
    ConvCfg(1,16,35280,64,8),
    ConvCfg(16,32,4410,32,8),
    ConvCfg(32,64,551,16,4),
    ConvCfg(64,256,137,4,None),
)

BASELINE_FLATTEN=35072
REDUCED_FLATTEN=8704
DENSE_DIMS=(128,64,2)

def validate():
    assert SOURCE_CONV[0].pool_out_length==4410
    assert SOURCE_CONV[1].pool_out_length==551
    assert SOURCE_CONV[2].pool_out_length==137
    assert SOURCE_CONV[3].cout*SOURCE_CONV[3].length==BASELINE_FLATTEN
    assert SOURCE_CONV[3].cout*(SOURCE_CONV[3].length//4)==REDUCED_FLATTEN
    return True
