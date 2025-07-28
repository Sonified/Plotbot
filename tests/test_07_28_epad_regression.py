#!/usr/bin/env python3

# Quick test to reproduce the epad plotting regression
print("Testing epad plotting regression...")

import sys
import os

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plotbot import *
import numpy as np

# Set up the exact same test case as user reported
trange = ['2018-10-22 12:00:00', '2018-10-27 13:00:00']

print(f"Testing plotbot call with trange: {trange}")
print("Calling plotbot(trange, mag_rtn_4sa.br, 1, epad.strahl, 2)")

try:
    plotbot(trange, mag_rtn_4sa.br, 1, epad.strahl, 2)
    print("✅ SUCCESS: epad plotting worked!")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc() 