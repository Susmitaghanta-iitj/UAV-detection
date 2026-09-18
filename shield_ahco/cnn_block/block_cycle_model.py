from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BlockCycles:
    conv_mac_cycles:int
    pool_compare_cycles:int
    writes:int
    total:int

def estimate_conv_pool(cin,cout,length,kernel,pool,macs_per_cycle=1):
    conv_out_len=length
    macs=cout*conv_out_len*cin*kernel
    conv_cycles=(macs+macs_per_cycle-1)//macs_per_cycle
    pool_out_len=conv_out_len//pool
    pool_compares=cout*pool_out_len*(pool-1)
    writes=cout*pool_out_len
    return BlockCycles(conv_cycles,pool_compares,writes,
                       conv_cycles+pool_compares+writes)

def thesis_first_three_pool_lengths():
    return {
        "input":35280,
        "after_pool1":35280//8,
        "after_pool2":(35280//8)//8,
        "after_pool3":((35280//8)//8)//4,
    }
