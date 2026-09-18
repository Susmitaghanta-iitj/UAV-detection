from shield_ahco.ahco_top.source_config import SOURCE_CONV,BASELINE_FLATTEN,REDUCED_FLATTEN,DENSE_DIMS,validate
assert validate()
assert [x.pool_out_length for x in SOURCE_CONV[:3]]==[4410,551,137]
assert BASELINE_FLATTEN==35072
assert REDUCED_FLATTEN==8704
assert DENSE_DIMS==(128,64,2)
print("AHCO configuration AHCO source configuration checks passed")
