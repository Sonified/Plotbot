#!/usr/bin/env python3
"""
Test for the exact issue in inconsistent-cells-FIXED.ipynb:
- First plotbot() call works
- Redefine the custom variable
- Second plotbot() call with SAME trange shows "No Data Available"
"""

import numpy as np
import plotbot as pb
from plotbot import plotbot, mag_rtn_4sa, custom_variable, print_manager

# Enable debug
print_manager.show_status = True
print_manager.show_custom_debug = True

# Same trange for all calls
trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']

print("\n" + "="*80)
print("TEST: Same trange, redefined custom variable")
print("="*80)

# FIRST CALL - Define phi_B with one formula
print("\n📊 FIRST CALL - phi_B = arctan2(br, bn) + 180")
custom_variable('phi_B', lambda: np.degrees(np.arctan2(pb.mag_rtn_4sa.br, pb.mag_rtn_4sa.bn)) + 180)
pb.phi_B.color = 'purple'

plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 1, mag_rtn_4sa.bn, 1, pb.phi_B, 2)

print(f"\n✅ First call:")
print(f"   br: {len(mag_rtn_4sa.br.data)} points")
print(f"   phi_B: {len(pb.phi_B.data)} points")

# REDEFINE phi_B with different formula
print("\n📊 SECOND CALL - REDEFINE phi_B = arctan2(br, bn) WITHOUT +180")
custom_variable('phi_B', lambda: np.degrees(np.arctan2(pb.mag_rtn_4sa.br, pb.mag_rtn_4sa.bn)))
pb.phi_B.color = 'purple'

# SECOND CALL - Same trange but redefined variable
plotbot(trange, mag_rtn_4sa.br, 1, pb.phi_B, 2)

print(f"\n✅ Second call:")
print(f"   br: {len(mag_rtn_4sa.br.data)} points")
print(f"   phi_B: {len(pb.phi_B.data)} points")

# THIRD CALL - Same trange, same variable (not redefined)
print("\n📊 THIRD CALL - Same trange, phi_B NOT redefined")
plotbot(trange, mag_rtn_4sa.br, 1, pb.phi_B, 2)

print(f"\n✅ Third call:")
print(f"   br: {len(mag_rtn_4sa.br.data)} points")
print(f"   phi_B: {len(pb.phi_B.data)} points")

print("\n" + "="*80)
print("ISSUE: If phi_B has 0 points on calls 2 or 3, that's the bug!")
print("="*80)

