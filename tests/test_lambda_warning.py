#!/usr/bin/env python3
"""
Test the lambda warning system for custom_variable.

This should print warnings for complex expressions that need lambda.
"""

import sys
import numpy as np

# Setup plotbot
import plotbot
from plotbot import print_manager

# Show status messages
print_manager.show_status = True
print_manager.show_warning = True
print_manager.show_custom_debug = False

print("=" * 60)
print("Testing Lambda Warning System")
print("=" * 60)

# Test 1: Simple operation (should NOT warn) - division by scalar
print("\n1️⃣ TEST 1: Simple scalar division (should NOT warn)")
print("-" * 60)
temp_kev = plotbot.custom_variable('temp_kev', plotbot.proton.temperature / 1000)
print("✅ Test 1 complete\n")

# Test 2: Simple ratio (should NOT warn) - single division operation
print("\n2️⃣ TEST 2: Simple ratio (should NOT warn)")
print("-" * 60)
simple_ratio = plotbot.custom_variable('simple_ratio', plotbot.proton.temperature / plotbot.mag_rtn_4sa.bmag)
print("✅ Test 2 complete\n")

# Test 3: Binary operation - add (SHOULD warn)
print("\n3️⃣ TEST 3: Binary operation - addition (SHOULD warn)")
print("-" * 60)
binary_add = plotbot.custom_variable('binary_add', plotbot.proton.temperature + plotbot.proton.density)
print("✅ Test 3 complete\n")

# Test 4: Chained operations (SHOULD warn)
print("\n4️⃣ TEST 4: Chained operations (SHOULD warn)")
print("-" * 60)
chained = plotbot.custom_variable('chained', (plotbot.proton.temperature / plotbot.mag_rtn_4sa.br) + plotbot.proton.density)
print("✅ Test 4 complete\n")

# Test 5: NumPy function (SHOULD warn)
print("\n5️⃣ TEST 5: NumPy arctan2 function (SHOULD warn)")
print("-" * 60)
numpy_func = plotbot.custom_variable('numpy_arctan', np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn))
print("✅ Test 5 complete\n")

# Test 6: Lambda expression (should NOT warn - it's correct!)
print("\n6️⃣ TEST 6: Lambda expression (should NOT warn - correct usage)")
print("-" * 60)
lambda_correct = plotbot.custom_variable('lambda_correct', lambda: np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180)
print("✅ Test 6 complete\n")

print("\n" + "=" * 60)
print("All tests complete!")
print("=" * 60)
print("\n📊 Expected results:")
print("  ✅ Tests 1, 2, 6 should NOT warn (simple/correct usage)")
print("  ⚠️  Tests 3, 4, 5 should WARN (complex expressions need lambda)")

