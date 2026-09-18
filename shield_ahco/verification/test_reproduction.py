from shield_ahco.repro.collect_static import collect
from shield_ahco.repro.targets import TARGETS
from shield_ahco.repro.compare_targets import compare

r=collect()
assert r["flatten_baseline"]==35072
assert r["flatten_reduced"]==8704
assert r["conv_macs"]==135413760
rows=compare(TARGETS,r)
assert any(x["metric"]=="flatten_baseline" and x["status"]=="matched" for x in rows)
assert any(x["metric"]=="fpga_power" and x["status"]=="pending" for x in rows)
print("reproduction harness reproduction harness checks passed")
