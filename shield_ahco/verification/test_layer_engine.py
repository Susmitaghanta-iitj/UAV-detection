from shield_ahco.bitaccurate.canonical import TPMode
from shield_ahco.cycle_model.executor import dense_codes,conv1d_codes,maxpool1d_codes
from shield_ahco.cycle_model.layer_model import dense_serialization_reduction

mode=TPMode.POSIT4_1
x=[0x4,0x5]
w=[0x4,0x4,0x5,0x3]
b=[0,0]
y=dense_codes(x,w,b,2,2,mode,True)
assert y == [0x5,0x5]  # exact 3 is halfway between 2 and 4; current tie rule selects 2.

x=[0x4,0x5,0x3]; w=[0x4]
assert conv1d_codes(x,w,[0],1,1,3,1,mode)==x
assert maxpool1d_codes([0x3,0x5,0x4,0x6],1,4,mode,2,2)==[0x5,0x6]

r=dense_serialization_reduction()
assert r["before"]==35072 and r["after"]==8704
assert 0.75 < r["reduction_fraction"] < 0.752
print("layer engine layer-engine software tests passed")
