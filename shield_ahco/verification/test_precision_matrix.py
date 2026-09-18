import torch
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline
from shield_ahco.experiments.quantized_model import quantize_source_model
from shield_ahco.experiments.precision_metadata import PRECISIONS

m=make_thesis_baseline(True,True).eval()
x=torch.randn(1,1,35280)

for p in PRECISIONS:
    qm=quantize_source_model(m,p,True).eval()
    with torch.no_grad():
        y=qm(x)
    assert y.shape==(1,2)
    assert torch.isfinite(y).all(), p
    print(p, y.detach().cpu().numpy().tolist())

print("precision matrix precision-matrix smoke tests passed")
