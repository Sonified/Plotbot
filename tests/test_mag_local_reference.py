#!/usr/bin/env python3
"""
Test if mag_rtn_4sa works with local references after plotbot() updates
"""

import plotbot
from plotbot import *

print_manager.show_status = True

trange = ['2023-09-28/06:00:00', '2023-09-28/07:00:00']

# Store LOCAL reference BEFORE plotbot loads data
print("Getting local reference to mag_rtn_4sa.br BEFORE plotbot()...")
my_br = mag_rtn_4sa.br
print(f"my_br ID: {id(my_br)}")
print(f"my_br has data: {hasattr(my_br, 'data')}")
print(f"my_br data shape: {my_br.data.shape if hasattr(my_br, 'data') else 'N/A'}")

# Now call plotbot to load data
print("\nCalling plotbot()...")
plotbot(trange, mag_rtn_4sa.br, 1)

# Check both local reference and global instance
print("\n" + "=" * 60)
print("AFTER plotbot():")
print("=" * 60)
print(f"\nGLOBAL mag_rtn_4sa.br ID: {id(mag_rtn_4sa.br)}")
print(f"GLOBAL mag_rtn_4sa.br data shape: {mag_rtn_4sa.br.data.shape}")

print(f"\nLOCAL my_br ID: {id(my_br)}")
print(f"LOCAL my_br data shape: {my_br.data.shape}")

if id(my_br) == id(mag_rtn_4sa.br):
    print("\n✅ SAME OBJECT - Local reference was updated!")
else:
    print("\n❌ DIFFERENT OBJECTS - Local reference is stale!")
    print(f"   Local has {my_br.data.shape[0]} points")
    print(f"   Global has {mag_rtn_4sa.br.data.shape[0]} points")

