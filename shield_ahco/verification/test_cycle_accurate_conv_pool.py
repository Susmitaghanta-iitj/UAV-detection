from shield_ahco.cycle_accurate_conv_pool.conv_pool_cycle_model import run_block
from shield_ahco.complete_layer.complete_layer_reference import LayerQuantMeta

meta=LayerQuantMeta(scale_aw_q=3107,scale_al_q=-394758,bias_q=[0,0],
                    alpha_q=100663296,out_scale_q=394758,frac_bits=24)
x=[10,20,30,40,50,60,70,80]
w=[128,129,130, 125,126,127]
r=run_block(x,w,meta,1,2,8,3,2,padding=1)
assert len(r.conv_codes)==16
assert len(r.pool_codes)==8
assert r.total_cycles>r.conv_cycles
assert all(0<=q<=255 for q in r.pool_codes)
print("cycle-accurate Conv->Pool Python model passed")
print("conv cycles",r.conv_cycles,"pool cycles",r.pool_cycles,"total",r.total_cycles)
