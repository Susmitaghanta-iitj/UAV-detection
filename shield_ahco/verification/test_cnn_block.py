from pathlib import Path
from tempfile import TemporaryDirectory
from shield_ahco.cnn_block.generate_two_block_case import gen
from shield_ahco.cnn_block.block_cycle_model import estimate_conv_pool,thesis_first_three_pool_lengths

with TemporaryDirectory() as td:
    p=gen(td,seed=9)
    b1=p["block1"]; b2=p["block2"]

    assert len(b1["pool_out"]) == b1["cout"]*b1["pool_len"]
    assert b2["input"] == b1["pool_out"]
    assert len(b2["pool_out"]) == b2["cout"]*b2["pool_len"]

    c=estimate_conv_pool(1,4,32,3,2)
    assert c.total > 0

    t=thesis_first_three_pool_lengths()
    assert t["after_pool1"]==4410
    assert t["after_pool2"]==551
    assert t["after_pool3"]==137

print("CNN-block integration two-block Python/scheduler-model checks passed")
