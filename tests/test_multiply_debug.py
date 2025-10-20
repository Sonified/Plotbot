#!/usr/bin/env python3
"""
Debug why br * bt fails but np.degrees(np.arctan2(br, bn)) works
"""

import numpy as np
import plotbot
from plotbot import print_manager

print_manager.show_status = True
print_manager.show_custom_debug = True

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

print("=" * 80)
print("TEST 1: Using np.multiply (NumPy ufunc)")
print("=" * 80)
b_product_numpy = plotbot.custom_variable('b_product_numpy', 
                                          lambda: np.multiply(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bt))

print("\n" + "=" * 80)
print("TEST 2: Using * operator (Python operator)")
print("=" * 80)
b_product_mult = plotbot.custom_variable('b_product_mult', 
                                        lambda: plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt)

print("\n" + "=" * 80)
print("Calling plotbot()...")
print("=" * 80)
result = plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                         b_product_numpy, 2, b_product_mult, 3)

print("\n" + "=" * 80)
print("RESULTS:")
print("=" * 80)
print(f"br shape: {plotbot.mag_rtn_4sa.br.data.shape}")
print(f"bt shape: {plotbot.mag_rtn_4sa.bt.data.shape}")
print(f"b_product_numpy shape: {b_product_numpy.data.shape}")
print(f"b_product_mult shape: {b_product_mult.data.shape}")

print(f"\nbr[:5]: {plotbot.mag_rtn_4sa.br.data[:5]}")
print(f"bt[:5]: {plotbot.mag_rtn_4sa.bt.data[:5]}")

if b_product_numpy.data.shape[0] > 0:
    print(f"b_product_numpy[:5]: {b_product_numpy.data[:5]}")
else:
    print(f"b_product_numpy: EMPTY ARRAY")

if b_product_mult.data.shape[0] > 0:
    print(f"b_product_mult[:5]: {b_product_mult.data[:5]}")
else:
    print(f"b_product_mult: EMPTY ARRAY")

expected = plotbot.mag_rtn_4sa.br.data * plotbot.mag_rtn_4sa.bt.data
print(f"expected[:5]: {expected[:5]}")

print("\n" + "=" * 80)
if b_product_numpy.data.shape == expected.shape and np.allclose(b_product_numpy.data, expected, rtol=1e-9, equal_nan=True):
    print("✅ np.multiply works!")
else:
    print("❌ np.multiply FAILS!")

if b_product_mult.data.shape == expected.shape and np.allclose(b_product_mult.data, expected, rtol=1e-9, equal_nan=True):
    print("✅ * operator works!")
else:
    print("❌ * operator FAILS!")

