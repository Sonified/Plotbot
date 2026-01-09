# tests/test_single_variable_multiplot.py
# Test for basic single-variable multiplot (the one that was broken)
# To run: conda run -n plotbot_env python tests/test_single_variable_multiplot.py

"""
Tests single-variable multiplot to verify the data refresh fix.
This was broken due to stale variable references after Loop 1 merges.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot as pb

print("=" * 60)
print("Testing single-variable multiplot")
print("=" * 60)

# Seven encounters from the notebook
rainbow_encounters = [
    {'perihelion': '2022/06/01 22:51:00.000'},  #Enc 12
    {'perihelion': '2022/09/06 06:04:00.000'},  #Enc 13
    {'perihelion': '2022/12/11 13:16:00.000'},  #Enc 14
    {'perihelion': '2023/03/17 20:30:00.000'},  #Enc 15
    {'perihelion': '2023/06/22 03:46:00.000'},  #Enc 16
    {'perihelion': '2023/09/27 23:28:00.000'},  #Enc 17
    {'perihelion': '2023/12/29 00:56:00.000'},  #Enc 18
]

# RESET PLOTTING OPTIONS
print("\n1. Resetting and configuring multiplot options...")
pb.plt.options.reset()

# Configure multiplot options
pb.plt.options.use_single_title = True
pb.plt.options.single_title_text = "PSP FIELDS Mag RTN Around Perihelion for Multiple Encounters"

pb.plt.options.y_label_uses_encounter = True
pb.plt.options.y_label_includes_time = False

pb.plt.options.window = '24:00:00.000'  # 24 hours total = ±12 hours around perihelion
pb.plt.options.position = 'around'

pb.plt.options.use_relative_time = True
pb.plt.options.relative_time_step_units = 'hours'
pb.plt.options.relative_time_step = 1

pb.plt.options.draw_vertical_line = True
pb.plt.options.vertical_line_color = 'red'
pb.plt.options.vertical_line_style = '--'

# Create plot data with single variable
print("\n2. Creating single-variable multiplot (br only)...")

try:
    plot_variable = pb.mag_rtn_4sa.br
    plot_data = [(encounter['perihelion'], plot_variable) for encounter in rainbow_encounters]

    fig, axs = pb.multiplot(plot_data)

    print("\n✅ SUCCESS! Single-variable multiplot completed.")
    print("   - Compares magnetic field at perihelion for E12-E18")
    print("   - Window: ±12 hours around perihelion")
    print("   - Each panel shows: Br (radial)")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
