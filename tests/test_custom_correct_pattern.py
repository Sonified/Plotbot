#!/usr/bin/env python3
"""
Test custom variables using the CORRECT access pattern (via global namespace)
"""

import plotbot as pb_module  # Import module with different name
from plotbot import *  # This imports the function 'plotbot'
from plotbot.data_classes.custom_variables import custom_variable
import numpy as np

print_manager.show_status = True

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

print("=" * 80)
print("TEST: Custom variables with CORRECT access pattern")
print("=" * 80)

# Create custom variable (returns placeholder/initial object)
print("\n1️⃣ Creating b_product (direct expression)...")
custom_variable('b_product', mag_rtn_4sa.br * mag_rtn_4sa.bt)

# Set styling on the GLOBAL reference
pb_module.b_product.color = 'green'

# Call plotbot with the GLOBAL reference
print("\n2️⃣ Calling plotbot() with GLOBAL reference...")
plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 1, pb_module.b_product, 2)

# Access data via GLOBAL namespace (correct pattern!)
print("\n" + "=" * 80)
print("RESULTS (accessing via GLOBAL namespace):")
print("=" * 80)

br_data = mag_rtn_4sa.br.data  # Global instance
bt_data = mag_rtn_4sa.bt.data  # Global instance
b_product_data = pb_module.b_product.data  # Global namespace!

print(f"br shape:        {br_data.shape}")
print(f"bt shape:        {bt_data.shape}")
print(f"b_product shape: {b_product_data.shape}")

if b_product_data.shape[0] >= 5:
    print(f"\nbr[:5]:        {br_data[:5]}")
    print(f"bt[:5]:        {bt_data[:5]}")
    print(f"b_product[:5]: {b_product_data[:5]}")
    
    expected = br_data * bt_data
    print(f"expected[:5]:  {expected[:5]}")
    
    if np.allclose(b_product_data, expected, rtol=1e-9, equal_nan=True):
        print("\n✅ SUCCESS! Custom variable works correctly!")
        print("   (When accessed via plotbot.b_product global namespace)")
    else:
        print("\n❌ VALUES DON'T MATCH")
else:
    print(f"\n❌ FAIL! Empty or wrong shape: {b_product_data.shape}")

