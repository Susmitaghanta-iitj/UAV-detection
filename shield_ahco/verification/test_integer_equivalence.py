import torch
from shield_ahco.qat.qat_layers import QATLinear
from shield_ahco.qat.paper_quantizers import LearnedWeightQuantizer,PACTActivation
from shield_ahco.golden.affine_int8 import AffineFormat,PACTFormat,encode,pact_encode
from shield_ahco.golden.qat_integer_mac import dot_affine_codes

lin=torch.nn.Linear(4,1,bias=True)
ql=QATLinear(lin,8).eval()

x=torch.tensor([0.1,0.5,1.0,2.0])
with torch.no_grad():
    y_ref=ql(x.unsqueeze(0)).item()

low=float(torch.minimum(ql.wq.low,ql.wq.high-1e-6))
high=float(torch.maximum(ql.wq.high,ql.wq.low+1e-6))
wf=AffineFormat(8,low,high)
af=PACTFormat(8,float(ql.aq.alpha))
qa=[pact_encode(float(v),af) for v in x]
qw=[encode(float(v),wf) for v in ql.weight[0]]
trace=dot_affine_codes(qa,qw,af,wf,float(ql.bias[0]))

assert abs(y_ref-trace.output_float) < 1e-5, (y_ref,trace.output_float)
print("QAT-to-RTL equivalence QAT integer equivalence test passed")
print("ref =",y_ref,"integer =",trace.output_float)
