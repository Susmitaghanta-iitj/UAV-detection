from shield_ahco.models.architecture_profiles import THESIS_BASELINE,trace_profile,pruning_consistency
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline

tr,flat=trace_profile(THESIS_BASELINE)
assert THESIS_BASELINE.input_length==35280
assert tr[-1]["channels"]==256
assert tr[-1]["length"]==137
assert flat==35072

b=make_thesis_baseline(False)
assert b.feature_shape==(1,256,137) and b.flatten_dim==35072
p=make_thesis_baseline(True,True)
assert p.feature_shape==(1,256,34) and p.flatten_dim==8704
l=make_thesis_baseline(True,False)
assert l.feature_shape==(1,256,17) and l.flatten_dim==4352

c=pruning_consistency()
assert c["baseline_flatten"]==35072
assert c["claim_consistent_pool4_flatten"]==8704
assert c["figure3_3_literal_pool8_flatten"]==4352
print("source reconciliation exact-shape reconstruction tests passed")
