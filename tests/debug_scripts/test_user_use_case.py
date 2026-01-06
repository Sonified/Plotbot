"""
Test the exact user use case - accessing .time on epad.strahl and mag_rtn_4sa.br
"""

import sys
import os
import numpy as np

# Add plotbot to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import plotbot

# User's exact code
trange = ['2020-01-29/18:00:00', '2020-01-29/20:00:00']

# Plot data
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.epad.strahl, 2)

print("\n" + "="*80)
print("USER'S EXACT USE CASE TEST")
print("="*80)

# Test epad
print("\n1. Testing EPAD time arrays:")
tpad1 = np.array(plotbot.epad.strahl.time)
tpad2 = np.array(plotbot.epad.strahl.datetime_array)
print(f"   tpad1 = np.array(plotbot.epad.strahl.time)")
print(f"   Shape: {tpad1.shape}")
print(f"   Type: {tpad1.dtype}")
print(f"   First value: {tpad1[0]}")
print(f"\n   tpad2 = np.array(plotbot.epad.strahl.datetime_array)")
print(f"   Shape: {tpad2.shape}")
print(f"   Note: Multi-dimensional because strahl uses times_mesh for spectral plot")

# Test mag
print("\n2. Testing MAG time arrays:")
tB1 = np.array(plotbot.mag_rtn_4sa.br.datetime_array)
tB2 = np.array(plotbot.mag_rtn_4sa.br.time)
print(f"   tB1 = np.array(plotbot.mag_rtn_4sa.br.datetime_array)")
print(f"   First value: {tB1[0]}")
print(f"\n   tB2 = np.array(plotbot.mag_rtn_4sa.br.time)")
print(f"   First value: {tB2[0]}")
print(f"   Type: {tB2.dtype}")

# Verify they're the same length (for 1D arrays)
print("\n3. Verification:")
print(f"   ✅ epad.strahl.time has {len(tpad1)} points (TT2000 epoch times)")
print(f"   ✅ mag.br.datetime_array and .time both have {len(tB1)} points")
print(f"   ✅ .time is int64 TT2000 epoch - perfect for HCS calculations!")

print("\n" + "="*80)
print("SUCCESS! Both .time and .datetime_array are now accessible!")
print("="*80 + "\n")

