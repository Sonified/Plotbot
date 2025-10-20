#!/usr/bin/env python3
"""
Test if simple binary operations (br * bt, temperature + density) work correctly 
WITHOUT lambda, or if they need lambda.

This will actually load data and compare results.
"""

import sys
import numpy as np

# Setup plotbot
import plotbot
from plotbot import print_manager

# Keep it quiet
print_manager.show_status = False
print_manager.show_warning = False
print_manager.show_custom_debug = False

print("=" * 80)
print("Testing Simple Binary Operations: Do they need lambda?")
print("=" * 80)

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

# Test 1: br * bt without lambda
print("\n📊 TEST 1: br × bt (multiplication) - NO LAMBDA")
print("-" * 80)
b_product_no_lambda = plotbot.custom_variable('b_product_no_lambda', 
                                               plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt)

# Test 2: br * bt WITH lambda
print("\n📊 TEST 2: br × bt (multiplication) - WITH LAMBDA")
print("-" * 80)
b_product_lambda = plotbot.custom_variable('b_product_lambda', 
                                           lambda: plotbot.mag_rtn_4sa.br * plotbot.mag_rtn_4sa.bt)

# Load data for both
print("\n🔄 Loading data for FIRST time range...")
print("-" * 80)
print_manager.show_status = True
result1 = plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1, 
                          b_product_no_lambda, 2, b_product_lambda, 3)
print_manager.show_status = False

# Get the data
br_data = plotbot.mag_rtn_4sa.br.data
bt_data = plotbot.mag_rtn_4sa.bt.data
no_lambda_data = b_product_no_lambda.data
lambda_data = b_product_lambda.data

print("\n📈 DATA SHAPES:")
print(f"  br shape: {br_data.shape}")
print(f"  bt shape: {bt_data.shape}")
print(f"  no_lambda shape: {no_lambda_data.shape}")
print(f"  lambda shape: {lambda_data.shape}")

# Calculate expected result
expected = br_data * bt_data

print("\n🔍 COMPARISON:")
print(f"  Expected (br × bt): shape={expected.shape}, sample values={expected[:5]}")
print(f"  No Lambda result:   shape={no_lambda_data.shape}, sample values={no_lambda_data[:5]}")
print(f"  Lambda result:      shape={lambda_data.shape}, sample values={lambda_data[:5]}")

# Check if they match
no_lambda_matches = np.allclose(no_lambda_data, expected, rtol=1e-9, equal_nan=True)
lambda_matches = np.allclose(lambda_data, expected, rtol=1e-9, equal_nan=True)

print("\n✅ RESULTS:")
print(f"  No Lambda matches expected: {no_lambda_matches}")
print(f"  Lambda matches expected:    {lambda_matches}")

if no_lambda_matches and lambda_matches:
    print("\n🎉 BOTH WORK! Simple binary multiplication works without lambda!")
elif lambda_matches and not no_lambda_matches:
    print("\n⚠️  LAMBDA REQUIRED! No-lambda version failed!")
else:
    print("\n❌ BOTH FAILED or unexpected result!")

# Now test with a DIFFERENT time range to see if they update correctly
print("\n" + "=" * 80)
print("🔄 Testing with DIFFERENT time range...")
print("=" * 80)
trange2 = ['2023-09-28/07:00:00', '2023-09-28/08:00:00']

print_manager.show_status = True
result2 = plotbot.plotbot(trange2, plotbot.mag_rtn_4sa.br, 1, plotbot.mag_rtn_4sa.bt, 1,
                          b_product_no_lambda, 2, b_product_lambda, 3)
print_manager.show_status = False

# Get the NEW data
br_data2 = plotbot.mag_rtn_4sa.br.data
bt_data2 = plotbot.mag_rtn_4sa.bt.data
no_lambda_data2 = b_product_no_lambda.data
lambda_data2 = b_product_lambda.data

print("\n📈 NEW DATA SHAPES:")
print(f"  br shape: {br_data2.shape}")
print(f"  bt shape: {bt_data2.shape}")
print(f"  no_lambda shape: {no_lambda_data2.shape}")
print(f"  lambda shape: {lambda_data2.shape}")

# Calculate expected result for new range
expected2 = br_data2 * bt_data2

print("\n🔍 COMPARISON (new time range):")
print(f"  Expected (br × bt): shape={expected2.shape}, sample values={expected2[:5]}")
print(f"  No Lambda result:   shape={no_lambda_data2.shape}, sample values={no_lambda_data2[:5]}")
print(f"  Lambda result:      shape={lambda_data2.shape}, sample values={lambda_data2[:5]}")

# Check if they match for the new range
no_lambda_matches2 = np.allclose(no_lambda_data2, expected2, rtol=1e-9, equal_nan=True)
lambda_matches2 = np.allclose(lambda_data2, expected2, rtol=1e-9, equal_nan=True)

print("\n✅ RESULTS (new time range):")
print(f"  No Lambda matches expected: {no_lambda_matches2}")
print(f"  Lambda matches expected:    {lambda_matches2}")

if no_lambda_matches2 and lambda_matches2:
    print("\n🎉 BOTH STILL WORK! Simple binary operations are fine without lambda!")
elif lambda_matches2 and not no_lambda_matches2:
    print("\n⚠️  LAMBDA REQUIRED! No-lambda version failed on second range!")
else:
    print("\n❌ BOTH FAILED on second range!")

# Final verdict
print("\n" + "=" * 80)
print("FINAL VERDICT:")
print("=" * 80)
if no_lambda_matches and no_lambda_matches2:
    print("✅ Simple binary operations (br × bt) work CORRECTLY without lambda!")
    print("   The notebook examples were over-cautious and should be updated.")
else:
    print("⚠️  Simple binary operations REQUIRE lambda for correct results!")
    print("   The notebook examples were correct.")

