#!/usr/bin/env python3
"""
Test using EXACT code from the notebook example
"""

import plotbot
from plotbot import *
from plotbot.data_classes.custom_variables import custom_variable
import numpy as np

# Same setup as notebook
print_manager.show_status = True
print_manager.show_warning = False
print_manager.show_custom_debug = False

# Define time range
trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

# Example 2 from notebook: Multiplication of magnetic field components (needs lambda!)
b_product = custom_variable('b_product', lambda: mag_rtn_4sa.br * mag_rtn_4sa.bt)
b_product.color = 'green'
b_product.legend_label = 'Br × Bt'

# Plot it
plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 1, b_product, 2)

# Check the results
print("\n" + "=" * 60)
print("CHECKING DATA:")
print("=" * 60)
print(f"br shape: {mag_rtn_4sa.br.data.shape}")
print(f"bt shape: {mag_rtn_4sa.bt.data.shape}")
print(f"b_product shape: {b_product.data.shape}")

if b_product.data.shape[0] > 0:
    print(f"\nbr[:5]: {mag_rtn_4sa.br.data[:5]}")
    print(f"bt[:5]: {mag_rtn_4sa.bt.data[:5]}")
    print(f"b_product[:5]: {b_product.data[:5]}")
    
    expected = mag_rtn_4sa.br.data * mag_rtn_4sa.bt.data
    print(f"expected[:5]: {expected[:5]}")
    
    if np.allclose(b_product.data, expected, rtol=1e-9, equal_nan=True):
        print("\n✅ SUCCESS! b_product matches expected br * bt")
    else:
        print("\n❌ FAIL! Values don't match")
else:
    print(f"\n❌ FAIL! b_product has empty data: shape={b_product.data.shape}")

