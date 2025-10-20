#!/usr/bin/env python3
"""
Test if br * bt works WITH lambda
"""

import numpy as np
import plotbot
from plotbot import print_manager

print_manager.show_status = True

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

print("Creating b_product WITH lambda...")
b_product = plotbot.custom_variable('b_product', lambda: plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt)

print("\nCalling plotbot()...")
result = plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, b_product, 2)

print("\n" + "=" * 60)
print("CHECKING DATA:")
print("=" * 60)
print(f"br shape: {plotbot.mag_rtn_4sa.br.data.shape}")
print(f"bt shape: {plotbot.mag_rtn_4sa.bt.data.shape}")
print(f"b_product shape: {b_product.data.shape}")

print(f"\nbr sample: {plotbot.mag_rtn_4sa.br.data[:5]}")
print(f"bt sample: {plotbot.mag_rtn_4sa.bt.data[:5]}")
print(f"b_product sample: {b_product.data[:5]}")

expected = plotbot.mag_rtn_4sa.br.data * plotbot.mag_rtn_4sa.bt.data
print(f"expected (br*bt) sample: {expected[:5]}")

if b_product.data.shape == expected.shape:
    if np.allclose(b_product.data, expected, rtol=1e-9, equal_nan=True):
        print("\n✅ SUCCESS! br * bt works WITH lambda!")
    else:
        print("\n❌ SHAPE matches but VALUES don't match!")
        print(f"Max diff: {np.max(np.abs(b_product.data - expected))}")
else:
    print(f"\n❌ FAIL! Shape mismatch: {b_product.data.shape} vs {expected.shape}")

