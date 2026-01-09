# tests/test_multiplot_right_axis.py
# Test for multiplot with second variable on right axis
# To run: conda run -n plotbot_env python tests/test_multiplot_right_axis.py

"""
Tests the second_variable_on_right_axis feature in multiplot.
This allows plotting two variables in the same panel with separate y-axes.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import plotbot as pb

print("=" * 60)
print("Testing multiplot with second_variable_on_right_axis")
print("=" * 60)

# Perihelion times for encounters
encounters = [
    {'perihelion': '2021/01/17 17:40:00.000'},  # E7
    {'perihelion': '2021/04/29 08:48:00.000'},  # E8
    {'perihelion': '2021/08/09 19:11:00.000'},  # E9
    {'perihelion': '2021/11/21 08:23:00.000'}   # E10
]

# RESET PLOTTING OPTIONS
print("\n1. Resetting and configuring multiplot options...")
pb.plt.options.reset()

# Configure multiplot options
pb.plt.options.second_variable_on_right_axis = True
pb.plt.options.show_right_axis_label = False

pb.plt.options.use_single_title = True
pb.plt.options.single_title_text = "PSP Magnetic Field Components Around Perihelion"

pb.plt.options.y_label_uses_encounter = True
pb.plt.options.y_label_includes_time = False

pb.plt.options.window = '12:00:00.000'  # 12 hours total = ±6 hours around perihelion
pb.plt.options.position = 'around'

pb.plt.options.use_relative_time = True
pb.plt.options.relative_time_step_units = 'hours'
pb.plt.options.relative_time_step = 2

pb.plt.options.draw_vertical_line = True
pb.plt.options.vertical_line_color = 'red'
pb.plt.options.vertical_line_style = '--'

# Create plot data with dual axes
print("\n2. Creating dual-axis multiplot (br left, bt right)...")

try:
    plot_data = [(encounter['perihelion'], [pb.mag_rtn_4sa.br, pb.mag_rtn_4sa.bt]) for encounter in encounters]

    fig, axs = pb.multiplot(plot_data)

    print("\n✅ SUCCESS! Dual-axis multiplot completed.")
    print("   - Compares magnetic field at perihelion for E7, E8, E9, E10")
    print("   - Window: ±6 hours around perihelion")
    print("   - Each panel shows:")
    print("     • Left axis: Br (radial)")
    print("     • Right axis: Bt (tangential)")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
