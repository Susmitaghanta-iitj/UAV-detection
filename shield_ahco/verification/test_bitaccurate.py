from shield_ahco.bitaccurate.fixed import FXP8_Q34, encode, decode
from shield_ahco.bitaccurate.posit import POSIT4_1, decode_bits, encode_nearest
from shield_ahco.bitaccurate.mac import dot_fxp8_q34, dot_posit

assert encode(7.9375,FXP8_Q34)==127
assert encode(-8.0,FXP8_Q34)==-128
assert decode(1,FXP8_Q34)==0.0625
assert decode_bits(0x1,POSIT4_1)==0.0625
assert decode_bits(0x4,POSIT4_1)==1.0
assert decode_bits(0x7,POSIT4_1)==16.0
assert encode_nearest(1.0,POSIT4_1)==0x4
assert abs(dot_fxp8_q34([1.5,-0.5],[2.0,4.0]).decoded-1.0)<1e-12
assert dot_posit([1.0],[2.0],POSIT4_1).decoded==2.0
print("bit-accurate arithmetic arithmetic smoke tests passed")
