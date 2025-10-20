#!/usr/bin/env python3
"""
Test if simple binary operations (br * bt) work correctly with and without lambda.
"""

import plotbot
from plotbot import *
from plotbot.data_classes.custom_variables import custom_variable
import numpy as np

# Proper print_manager setup
print_manager.show_status = True
print_manager.show_warning = True
print_manager.show_custom_debug = True  # THIS IS KEY!
print_manager.show_debug = False

print("=" * 80)
print("TEST: br * bt multiplication - WITH and WITHOUT lambda")
print("=" * 80)

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

# Test 1: WITHOUT lambda (direct expression)
print("\n1️⃣ Creating b_product_no_lambda (direct expression)...")
print("-" * 80)
b_product_no_lambda = custom_variable('b_product_no_lambda', mag_rtn_4sa.br * mag_rtn_4sa.bt)

# Test 2: WITH lambda
print("\n2️⃣ Creating b_product_lambda (lambda expression)...")
print("-" * 80)
b_product_lambda = custom_variable('b_product_lambda', lambda: mag_rtn_4sa.br * mag_rtn_4sa.bt)

# Load data
print("\n3️⃣ Calling plotbot() to load data...")
print("-" * 80)
plotbot(trange, mag_rtn_4sa.br, 1, mag_rtn_4sa.bt, 1, 
        b_product_no_lambda, 2, b_product_lambda, 3)

# Check results
print("\n" + "=" * 80)
print("RESULTS:")
print("=" * 80)

br_data = mag_rtn_4sa.br.data
bt_data = mag_rtn_4sa.bt.data
no_lambda_data = b_product_no_lambda.data
lambda_data = b_product_lambda.data

print(f"br shape:              {br_data.shape}")
print(f"bt shape:              {bt_data.shape}")
print(f"no_lambda shape:       {no_lambda_data.shape}")
print(f"lambda shape:          {lambda_data.shape}")

expected = br_data * bt_data

if no_lambda_data.shape[0] >= 5:
    print(f"\nbr[:5]:                {br_data[:5]}")
    print(f"bt[:5]:                {bt_data[:5]}")
    print(f"no_lambda[:5]:         {no_lambda_data[:5]}")
    print(f"expected (br*bt)[:5]:  {expected[:5]}")
else:
    print(f"\nno_lambda data:        {no_lambda_data}")

if lambda_data.shape[0] >= 5:
    print(f"lambda[:5]:            {lambda_data[:5]}")
else:
    print(f"lambda data:           {lambda_data}")

# Verdict
print("\n" + "=" * 80)
print("VERDICT:")
print("=" * 80)

no_lambda_works = (no_lambda_data.shape == expected.shape and 
                   np.allclose(no_lambda_data, expected, rtol=1e-9, equal_nan=True))
lambda_works = (lambda_data.shape == expected.shape and 
                np.allclose(lambda_data, expected, rtol=1e-9, equal_nan=True))

if no_lambda_works:
    print("✅ NO LAMBDA works!")
else:
    print("❌ NO LAMBDA fails!")

if lambda_works:
    print("✅ LAMBDA works!")
else:
    print("❌ LAMBDA fails!")

print("\n" + "=" * 80)
if no_lambda_works and lambda_works:
    print("🎉 BOTH WORK! Simple binary operations don't need lambda!")
elif lambda_works and not no_lambda_works:
    print("⚠️  LAMBDA REQUIRED for binary operations!")
elif no_lambda_works and not lambda_works:
    print("🤔 WEIRD: No-lambda works but lambda fails?!")
else:
    print("💥 BOTH FAIL - something is broken!")

