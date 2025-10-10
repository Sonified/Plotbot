#!/usr/bin/env python3
"""
Test that mimics the exact notebook behavior from inconsistent-cells-original.ipynb:
- Cell 1: Define phi_B
- Cell 2: First plotbot() call
- Cell 3: Redefine phi_B (different formula)
- Cell 4: Second plotbot() call (SAME trange)
- Cell 5: Third plotbot() call (DIFFERENT trange)

The issue: Cell 4 shows "No Data Available" for phi_B
"""

import numpy as np
import plotbot
from plotbot import print_manager

# Enable ALL debug output
print_manager.show_status = True
print_manager.show_custom_debug = True

print("\n" + "="*80)
print("NOTEBOOK BEHAVIOR TEST")
print("="*80)

# =============================================================================
# CELL 1: Define phi_B
# =============================================================================
print("\n" + "="*80)
print("CELL 1: Define phi_B")
print("="*80)
phi_B = plotbot.custom_variable(
    'phi_B',
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
)
phi_B.y_label = r'$\phi_B \ (\circ)$'
phi_B.color = 'purple'

print(f"\n📊 CELL 1 RESULT:")
print(f"   local phi_B ID: {id(phi_B)}")
print(f"   local phi_B data: {len(phi_B.data)} points")
print(f"   plotbot.phi_B ID: {id(plotbot.phi_B)}")
print(f"   plotbot.phi_B data: {len(plotbot.phi_B.data)} points")

# =============================================================================
# CELL 2: First plotbot() call
# =============================================================================
print("\n" + "="*80)
print("CELL 2: First plotbot() call")
print("="*80)
trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)

print(f"\n📊 CELL 2 RESULT:")
print(f"   local phi_B ID: {id(phi_B)}")
print(f"   local phi_B data: {len(phi_B.data)} points")
print(f"   plotbot.phi_B ID: {id(plotbot.phi_B)}")
print(f"   plotbot.phi_B data: {len(plotbot.phi_B.data)} points")
print(f"   mag_rtn_4sa.br data: {len(plotbot.mag_rtn_4sa.br.data)} points")

# =============================================================================
# CELL 3: Redefine phi_B (WITHOUT +180)
# =============================================================================
print("\n" + "="*80)
print("CELL 3: Redefine phi_B (WITHOUT +180)")
print("="*80)
phi_B = plotbot.custom_variable(
    'phi_B',
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
)
phi_B.y_label = r'$\phi_B \ (\circ)$'
phi_B.color = 'purple'

print(f"\n📊 CELL 3 RESULT:")
print(f"   local phi_B ID: {id(phi_B)}")
print(f"   local phi_B data: {len(phi_B.data)} points")
print(f"   plotbot.phi_B ID: {id(plotbot.phi_B)}")
print(f"   plotbot.phi_B data: {len(plotbot.phi_B.data)} points")

# =============================================================================
# CELL 4: Second plotbot() call (SAME TRANGE)
# =============================================================================
print("\n" + "="*80)
print("CELL 4: Second plotbot() call (SAME TRANGE)")
print("="*80)
trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)

print(f"\n📊 CELL 4 RESULT:")
print(f"   local phi_B ID: {id(phi_B)}")
print(f"   local phi_B data: {len(phi_B.data)} points")
print(f"   plotbot.phi_B ID: {id(plotbot.phi_B)}")
print(f"   plotbot.phi_B data: {len(plotbot.phi_B.data)} points")
print(f"   mag_rtn_4sa.br data: {len(plotbot.mag_rtn_4sa.br.data)} points")

# =============================================================================
# CELL 5: Third plotbot() call (DIFFERENT TRANGE)
# =============================================================================
print("\n" + "="*80)
print("CELL 5: Third plotbot() call (DIFFERENT TRANGE)")
print("="*80)
trange = ['2020-01-29/19:00:00', '2020-01-29/20:00:00']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)

print(f"\n📊 CELL 5 RESULT:")
print(f"   local phi_B ID: {id(phi_B)}")
print(f"   local phi_B data: {len(phi_B.data)} points")
print(f"   plotbot.phi_B ID: {id(plotbot.phi_B)}")
print(f"   plotbot.phi_B data: {len(plotbot.phi_B.data)} points")
print(f"   mag_rtn_4sa.br data: {len(plotbot.mag_rtn_4sa.br.data)} points")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("Expected behavior:")
print("  - Cell 2: phi_B should have data")
print("  - Cell 4: phi_B should have data (redefined, same trange)")
print("  - Cell 5: phi_B should have data (same definition, different trange)")
print("\n⚠️  If any cell shows 0 points for phi_B, that's the bug!")
print("="*80)

