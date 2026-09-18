from pathlib import Path
from tempfile import TemporaryDirectory
from shield_ahco.layer_coverify.generate_dense_case import generate_case as gen_dense
from shield_ahco.layer_coverify.generate_conv_case import generate_case as gen_conv
from shield_ahco.layer_coverify.python_layer_reference import dense_reference,conv_reference

with TemporaryDirectory() as td:
    td=Path(td)
    d=gen_dense(td,din=7,dout=5,seed=123)
    ref=dense_reference(td/"dense_case.json")
    assert ref==d["expected"]

    c=gen_conv(td,cin=2,cout=2,length=9,kernel=3,stride=1,padding=1,seed=456)
    refc=conv_reference(td/"conv_case.json")
    assert refc==c["expected"]

print("layer co-verification dense/conv Python layer-reference checks passed")
