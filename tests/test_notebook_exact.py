#!/usr/bin/env python3
"""
EXACT reproduction of inconsistent-cells-original.ipynb
"""

import numpy as np
import plotbot
from plotbot import print_manager

# Enable debug
print_manager.show_status = True
print_manager.show_custom_debug = True

print("\n" + "="*80)
print("CELL 1: Define phi_B")
print("="*80)
phi_B = plotbot.custom_variable(
    'phi_B',
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
) 
phi_B.y_label = r'$\phi_B \ (\circ)$'
phi_B.color = 'purple'
phi_B.plot_type = 'scatter'
phi_B.marker_style = 'o'
phi_B.marker_size = 3

print("\n" + "="*80)
print("CELL 2: First plotbot() call")
print("="*80)
trange = ['12-20-2024/00:00:000','12-24-2024/00:00:000']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)
print(f"✅ CELL 2: phi_B has {len(plotbot.phi_B.data)} points")

print("\n" + "="*80)
print("CELL 3: Redefine phi_B")
print("="*80)
phi_B = plotbot.custom_variable(
    'phi_B',
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
) 
phi_B.y_label = r'$\phi_B \ (\circ)$'
phi_B.color = 'purple'
phi_B.plot_type = 'scatter'
phi_B.marker_style = 'o'
phi_B.marker_size = 3

print("\n" + "="*80)
print("CELL 4: Second plotbot() call (SAME TRANGE)")
print("="*80)
trange = ['12-20-2024/00:00:000','12-24-2024/00:00:000']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)
print(f"✅ CELL 4: phi_B has {len(plotbot.phi_B.data)} points")

print("\n" + "="*80)
print("CELL 5: Third plotbot() call (DIFFERENT TRANGE)")
print("="*80)
trange = ['12-25-2024/00:00:000','12-26-2024/00:00:000']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                plotbot.mag_rtn_4sa.bn, 1, plotbot.phi_B, 2)
print(f"✅ CELL 5: phi_B has {len(plotbot.phi_B.data)} points")

print("\n" + "="*80)
print("🎉 ALL CELLS COMPLETED SUCCESSFULLY!")
print("="*80)

