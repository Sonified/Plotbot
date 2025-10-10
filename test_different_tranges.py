#!/usr/bin/env python3
"""
Test plotting same custom variable with DIFFERENT tranges.
This is what fails in the notebook.
"""

import numpy as np
import plotbot as pb
from plotbot import plotbot, mag_rtn_4sa, custom_variable

# Define phi_B once (old-style, no lambda)
phi_B = custom_variable('phi_B', np.degrees(np.arctan2(pb.mag_rtn_4sa.br, pb.mag_rtn_4sa.bn)) + 180)

print("\n" + "="*80)
print("TEST: Different tranges, SAME variable (not redefined)")
print("="*80)

# First trange
trange1 = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
print(f"\n📊 Call 1: {trange1}")
plotbot(trange1, mag_rtn_4sa.br, 1, pb.phi_B, 2)
br_len1 = len(mag_rtn_4sa.br.data)
phi_len1 = len(pb.phi_B.data)
print(f"Result: br={br_len1}, phi_B={phi_len1}")

# DIFFERENT trange (this should reload and recalculate!)
trange2 = ['2020-01-29/19:00:00', '2020-01-29/19:20:00']
print(f"\n📊 Call 2: {trange2} (DIFFERENT trange)")
plotbot(trange2, mag_rtn_4sa.br, 1, pb.phi_B, 2)
br_len2 = len(mag_rtn_4sa.br.data)
phi_len2 = len(pb.phi_B.data)
print(f"Result: br={br_len2}, phi_B={phi_len2}")

print("\n" + "="*80)
if phi_len1 > 0 and phi_len2 > 0 and phi_len1 != phi_len2:
    print("✅ SUCCESS! Both calls have data and different lengths")
elif phi_len2 == 0:
    print("❌ FAIL! Second call has NO DATA")
else:
    print(f"⚠️  Unexpected: phi_B lengths = {phi_len1}, {phi_len2}")
print("="*80)

