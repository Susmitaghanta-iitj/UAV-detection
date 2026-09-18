def dense_cycles_latency1(din,dout):
    # ISSUE + WAIT per tap + small control overhead (CLEAR + EMIT per output)
    return dout*(2*din + 2)

def dense_cycles_zero_latency(din,dout):
    return dout*din

def report(din=8704,dout=128):
    z=dense_cycles_zero_latency(din,dout)
    l=dense_cycles_latency1(din,dout)
    return {
        "zero_latency_assumption":z,
        "explicit_1cycle_sram":l,
        "ratio":l/z
    }

if __name__=="__main__":
    import json
    print(json.dumps(report(),indent=2))
