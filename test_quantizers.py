import torch
from shield_ahco.software.quantization.quantizers import (
    bf16_fake_quant, fxp8_q34_fake_quant,
    posit4_1_fake_quant, posit8_2_fake_quant,
    hfp4_e2m1_fake_quant, hfp4_e3m0_fake_quant
)

x = torch.tensor([-20., -16., -8., -1., -0.1, 0., 0.1, 1., 6., 8., 16., 20.])
print("BF16", bf16_fake_quant(x))
print("FXP8 Q3.4", fxp8_q34_fake_quant(x))
print("Posit(4,1)", posit4_1_fake_quant(x))
print("Posit(8,2)", posit8_2_fake_quant(x))
print("HFP4 E2M1", hfp4_e2m1_fake_quant(x))
print("HFP4 E3M0", hfp4_e3m0_fake_quant(x))
