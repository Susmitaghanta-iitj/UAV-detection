from pathlib import Path
from tempfile import TemporaryDirectory
from shield_ahco.complete_layer.generate_complete_layer_cases import gen_dense,gen_conv

with TemporaryDirectory() as td:
    td=Path(td)
    d=gen_dense(td,din=7,dout=3,seed=1)
    c=gen_conv(td,cin=2,cout=2,length=7,kernel=3,stride=1,padding=1,seed=2)
    assert len(d["out_codes"])==3
    assert len(c["out_codes"])==2
    assert len(c["out_codes"][0])==7
    assert all(0<=q<=255 for q in d["out_codes"])
    assert all(0<=q<=255 for row in c["out_codes"] for q in row)

print("complete layer complete-layer Python checks passed")
