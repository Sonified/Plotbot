#!/usr/bin/env python3
"""
Test to see all 12 debug steps for custom variables.
This will help identify where the flow breaks.
"""

import numpy as np
import plotbot as pb
from plotbot import plotbot, mag_rtn_4sa, custom_variable, print_manager

# Enable custom debug to see all 12 steps
print_manager.show_custom_debug = True

print("\n" + "="*80)
print("12-STEP DEBUG TEST")
print("="*80)

# Test 1: Direct expression (original working code)
print("\n" + "-"*80)
print("TEST 1: Direct Expression Variable")
print("-"*80)

# Create direct expression custom variable
phi_B_direct = custom_variable('phi_B_direct', np.abs(pb.mag_rtn_4sa.bn))
print("\n🔷 Variable created. Now plotting...\n")

# First trange
trange1 = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
print(f"\n📊 Trange 1: {trange1}")
plotbot(trange1, mag_rtn_4sa.br, 1, pb.phi_B_direct, 2)
print(f"✓ Result: br={len(mag_rtn_4sa.br.data)}, phi_B_direct={len(pb.phi_B_direct.data)}")

# DIFFERENT trange (this should show all 12 steps again)
trange2 = ['2020-01-29/19:00:00', '2020-01-29/19:20:00']
print(f"\n📊 Trange 2: {trange2} (DIFFERENT)")
plotbot(trange2, mag_rtn_4sa.br, 1, pb.phi_B_direct, 2)
print(f"✓ Result: br={len(mag_rtn_4sa.br.data)}, phi_B_direct={len(pb.phi_B_direct.data)}")

print("\n" + "="*80)
print("END OF TEST - Check debug output above for all 12 steps")
print("="*80)

