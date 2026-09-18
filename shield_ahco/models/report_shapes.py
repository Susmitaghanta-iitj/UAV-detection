import json
from shield_ahco.models.architecture_profiles import THESIS_BASELINE,trace_profile,pruning_consistency
from shield_ahco.models.source_aligned_1dfcnn import make_thesis_baseline

def main():
    tr,flat=trace_profile(THESIS_BASELINE)
    print("THESIS FIG.3.2 SHAPE TRACE")
    for row in tr: print(row)
    print("flatten =",flat)
    b=make_thesis_baseline(False)
    p=make_thesis_baseline(True,True)
    l=make_thesis_baseline(True,False)
    print("baseline:",b.feature_shape,b.flatten_dim)
    print("claim-consistent post-pruning:",p.feature_shape,p.flatten_dim)
    print("literal Fig.3.3 pool(8):",l.feature_shape,l.flatten_dim)
    print(json.dumps(pruning_consistency(),indent=2))
if __name__=="__main__": main()
