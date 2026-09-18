from shield_ahco.final_equiv.fixedpoint_metadata import make_fixed_meta
from shield_ahco.final_equiv.finalize_reference import exact_finalize,fixed_finalize

sa=6/255
sw=2/255
wlow=-1.0
bias=0.125
alpha=6.0

meta=make_fixed_meta(sa,sw,wlow,bias,alpha,8,24)

for s0,s1 in [(0,0),(12345,1200),(999999,4000),(2000000,10000)]:
    e=exact_finalize(s0,s1,sa,sw,wlow,bias,alpha,8)
    f=fixed_finalize(s0,s1,meta,8)
    assert 0 <= f.out_code <= 255
    assert abs(e.out_code-f.out_code) <= 1

print("final-output equivalence finalizer Python checks passed")
