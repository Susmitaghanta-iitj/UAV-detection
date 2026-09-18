import json
from pathlib import Path
from tempfile import TemporaryDirectory
from shield_ahco.coverify.generate_accum_vectors import gen_sequences

with TemporaryDirectory() as td:
    td=Path(td)
    data=gen_sequences(td,sequences=16,taps=17,seed=123)
    for m in data:
        ref0=sum(a*w for a,w in m["pairs"])
        ref1=sum(a for a,_ in m["pairs"])
        assert ref0==m["sum_qaqw"]
        assert ref1==m["sum_qa"]
print("MAC co-verification vector-generation and Python shadow checks passed")
