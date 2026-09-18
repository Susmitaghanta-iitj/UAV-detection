from shield_ahco.bitaccurate.canonical import TPMode, decode_to_canonical, encode_from_canonical
from shield_ahco.bitaccurate.transprecision_mac import dot_codes

# Identity-ish sanity tests in all modes
tests = [
    (TPMode.HFP4_E2M1, 0x3, 0x3),  # source codebook-dependent, just check finite
    (TPMode.HFP4_E3M0, 0x3, 0x3),
    (TPMode.POSIT4_1,  0x4, 0x5),  # 1 * 2 => 2
    (TPMode.POSIT8_2,  0x40, 0x40),
]
for mode,a,b in tests:
    c,v,acc,nar = dot_codes([a],[b],mode)
    assert not nar
    assert isinstance(c,int)
    assert isinstance(v,float)

c,v,acc,nar = dot_codes([0x4],[0x5],TPMode.POSIT4_1)
assert c == 0x5 and v == 2.0 and not nar

# Posit NaR propagation
c,v,acc,nar = dot_codes([0x8],[0x4],TPMode.POSIT4_1)
assert nar and c == 0x8

print("shared transprecision shared transprecision software tests passed")
