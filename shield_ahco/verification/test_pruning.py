import torch
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.pruning.structured_channel_pruning import count_conv_macs,dense_macs

b=make_thesis_baseline(False)
p=make_thesis_baseline(True,True)

assert b.flatten_dim==35072
assert p.flatten_dim==8704
assert dense_macs(p) < dense_macs(b)

# Forward smoke test with one waveform sample
x=torch.randn(1,1,35280)
with torch.no_grad():
    yb=b(x); yp=p(x)
assert yb.shape==(1,2) and yp.shape==(1,2)

print("pruning pruning/training smoke tests passed")
print("baseline dense MACs:",dense_macs(b))
print("reduced dense MACs :",dense_macs(p))
