from __future__ import annotations
from dataclasses import dataclass
from shield_ahco.complete_layer.complete_layer_reference import LayerQuantMeta
from shield_ahco.final_equiv.fixedpoint_metadata import FixedMeta
from shield_ahco.final_equiv.finalize_reference import fixed_finalize

@dataclass
class Result:
    conv_codes:list[int]
    pool_codes:list[int]
    conv_cycles:int
    pool_cycles:int
    total_cycles:int

def run_block(x,w,meta:LayerQuantMeta,cin,cout,length,kernel,pool,padding=1,stride=1):
    out_len=((length+2*padding-kernel)//stride)+1
    conv=[]
    cycles=0
    for oc in range(cout):
        for ox in range(out_len):
            s0=s1=0
            for ic in range(cin):
                for k in range(kernel):
                    ix=ox*stride+k-padding
                    qa=x[ic*length+ix] if 0<=ix<length else 0
                    qw=w[(oc*cin+ic)*kernel+k]
                    # ISSUE + WAIT + CONSUME
                    cycles += 3
                    s0 += qa*qw
                    s1 += qa
            fm=FixedMeta(meta.frac_bits,meta.scale_aw_q,meta.scale_al_q,
                         meta.bias_q[oc],meta.alpha_q,meta.out_scale_q)
            conv.append(fixed_finalize(s0,s1,fm,8).out_code)
            cycles += 2 # finalize + write

    conv_cycles=cycles
    pool_len=out_len//pool
    pooled=[]
    for c in range(cout):
        for ox in range(pool_len):
            best=0
            for k in range(pool):
                # ISSUE + WAIT + CONSUME
                cycles += 3
                best=max(best,conv[c*out_len+ox*pool+k])
            pooled.append(best)
            cycles += 1 # write
    return Result(conv,pooled,conv_cycles,cycles-conv_cycles,cycles)
