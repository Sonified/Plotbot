#!/usr/bin/env python3
"""
Test br * bt WITHOUT lambda (direct expression)
"""

import plotbot
from plotbot import *
from plotbot.data_classes.custom_variables import custom_variable
import numpy as np

print_manager.show_status = True

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

# WITHOUT lambda - direct expression
print("Creating b_product WITHOUT lambda (direct expression)...")
b_product = custom_variable('b_product', mag_rtn_4sa.br * mag_rtn_4sa.bt)
b_product.color = 'green'

print("\nCalling plotbot()...")
plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 1, b_product, 2)

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)
print(f"br shape: {mag_rtn_4sa.br.data.shape}")
print(f"bt shape: {mag_rtn_4sa.bt.data.shape}")
print(f"b_product shape: {b_product.data.shape}")

if b_product.data.shape[0] >= 5:
    print(f"\nbr[:5]: {mag_rtn_4sa.br.data[:5]}")
    print(f"bt[:5]: {mag_rtn_4sa.bt.data[:5]}")
    print(f"b_product[:5]: {b_product.data[:5]}")
    
    expected = mag_rtn_4sa.br.data * mag_rtn_4sa.bt.data
    print(f"expected[:5]: {expected[:5]}")
    
    if np.allclose(b_product.data, expected, rtol=1e-9, equal_nan=True):
        print("\n✅ SUCCESS! Direct expression works!")
    else:
        print("\n❌ VALUES DON'T MATCH")
else:
    print(f"\n❌ FAIL! Empty or wrong shape: {b_product.data.shape}")
    if b_product.data.shape[0] > 0:
        print(f"Data: {b_product.data}")

