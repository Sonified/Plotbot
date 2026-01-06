#!/usr/bin/env python3
"""
Test script to verify styling preservation during merge operations.
This tests the fix where we removed set_plot_config() from the merge path.
"""

from plotbot import *

print("🧪 STYLING PRESERVATION TEST")
print("=" * 60)

# Test with mag_rtn_4sa (proven working class)
print("\n📊 TEST 1: mag_rtn_4sa styling preservation")
print("-" * 60)

# Set custom styling
print("🎨 Setting custom styling...")
mag_rtn_4sa.br.color = "purple"
mag_rtn_4sa.br.legend_label = "Br Custom Purple"
print(f"   br: color={mag_rtn_4sa.br.color}, label='{mag_rtn_4sa.br.legend_label}'")

# First load
print("\n📈 First load (2021-04-29)...")
plotbot(['2021-04-29/06:00:00', '2021-04-29/12:00:00'], mag_rtn_4sa.br, 1)
print(f"   After first load: color={mag_rtn_4sa.br.color}, label='{mag_rtn_4sa.br.legend_label}'")

# Second load (different date - triggers MERGE)
print("\n📈 Second load (2021-04-30) - MERGE PATH...")
plotbot(['2021-04-30/06:00:00', '2021-04-30/12:00:00'], mag_rtn_4sa.br, 1)
print(f"   After merge: color={mag_rtn_4sa.br.color}, label='{mag_rtn_4sa.br.legend_label}'")

# Verify
if mag_rtn_4sa.br.color == "purple":
    print("   ✅ mag_rtn_4sa color PRESERVED!")
else:
    print(f"   ❌ mag_rtn_4sa color LOST (now {mag_rtn_4sa.br.color})")

print("\n" + "=" * 60)
print("🏁 TEST COMPLETE")
print("=" * 60)
