from shield_ahco.cycle_accurate_memory.cycle_accurate_model import DenseLatency1Model

din=5; dout=3
act=[1,2,3,4,5]
weight=[
    1,1,1,1,1,
    2,2,2,2,2,
    5,4,3,2,1,
]

m=DenseLatency1Model(act,weight,din,dout)
out=m.run()

exp=[
    (sum(act),sum(act)),
    (2*sum(act),sum(act)),
    (1*5+2*4+3*3+4*2+5*1,sum(act)),
]
assert out==exp
assert m.cycles==2*din*dout

print("cycle-accurate latency-1 SRAM model checks passed")
print("cycles:",m.cycles)
