import torch
from torch import nn
from shield_ahco.qat.paper_quantizers import PACTActivation,LearnedWeightQuantizer
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.qat.qat_layers import convert_to_qat

x=torch.tensor([-1.0,0.0,1.0,8.0])
p=PACTActivation(8,init_alpha=6.0)
y=p(x)
assert torch.isfinite(y).all()
assert y.min() >= 0

wq=LearnedWeightQuantizer(8,-1,1)
w=torch.linspace(-2,2,17)
qw=wq(w)
assert qw.min() >= -1.01 and qw.max() <= 1.01

m=make_thesis_baseline(True,True)
qm=convert_to_qat(m,8).eval()
with torch.no_grad():
    out=qm(torch.randn(1,1,35280))
assert out.shape==(1,2)
assert torch.isfinite(out).all()

print("QAT PACT/QAT smoke tests passed")
