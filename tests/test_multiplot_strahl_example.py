#!/usr/bin/env python3
"""
Test for multiplot that first shows a working example with mag_rtn_4sa.br,
and then shows the failing example with epad.strahl.
This allows for direct visual comparison and debugging.
"""

import sys
import os

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import necessary plotbot components
from plotbot import epad, multiplot, plt, mag_rtn_4sa
from plotbot.print_manager import print_manager

def plot_br_example():
    """
    Generates and shows a working multiplot with mag_rtn_4sa.br.
    """
    print("\n================================================================================")
    print("PLOT 1: Generating working example with mag_rtn_4sa.br...")
    print("================================================================================\n")
    
    # --- Reset plotting options ---
    plt.options.reset()
    
    # --- Configure General Plot Options ---
    plt.options.width = 20
    plt.options.height_per_panel = 3
    plt.options.hspace = .5
    plt.options.use_single_title = True
    plt.options.single_title_text = "WORKING EXAMPLE: Br Around PSP HCS Crossings"
    plt.options.draw_vertical_line = True
    
    # --- Data Selection ---
    hcs_crossing_times = [
        '2022-12-12/08:30:00.000',
        '2023-06-22/01:30:00.000',
        '2023-06-22/04:45:00.000'
    ]
    plt.options.window = '06:00:00.000'
    plt.options.position = 'around'
    plot_variable = mag_rtn_4sa.br
    
    plot_data = [(time, plot_variable) for time in hcs_crossing_times]
    
    # --- Call Multiplot and Show ---
    plt.options.show_plot = True  # Ensure plot is configured to be shown
    multiplot(plot_data)
    plt.show()  # This will block until you close the plot window

def plot_strahl_example():
    """
    Generates and shows the multiplot with epad.strahl that is currently failing.
    This is for visual inspection.
    """
    print("\n================================================================================")
    print("PLOT 2: Generating failing example with epad.strahl for debugging...")
    print("================================================================================\n")

    # --- Reset plotting options ---
    plt.options.reset()

    # --- Enable debug prints to diagnose the issue ---
    print_manager.show_debug = True
    print_manager.show_status = True

    # --- Configure General Plot Options from Notebook ---
    plt.options.width = 20
    plt.options.height_per_panel = 3
    plt.options.hspace = .5
    plt.options.use_single_title = True
    plt.options.single_title_text = "FAILING EXAMPLE: EPAD Strahl Around PSP HCS Crossings"
    plt.options.draw_vertical_line = True

    # --- Configure Axis-Specific Options ---
    plt.options.ax2.colorbar_limits = (9, 10.7)
    plt.options.ax3.colorbar_limits = (9, 10.7)
    
    # --- Ploptions ---
    epad.strahl.colorbar_limits = 'default'

    # --- Data Selection ---
    hcs_crossing_times = [
        '2022-12-12/08:30:00.000',
        '2023-06-22/01:30:00.000',
        '2023-06-22/04:45:00.000'
    ]
    plt.options.window = '06:00:00.000'
    plt.options.position = 'around'
    plot_variable = epad.strahl
    
    plot_data = [(time, plot_variable) for time in hcs_crossing_times]

    # --- Call Multiplot and Show ---
    plt.options.show_plot = True # Ensure plot is configured to be shown
    multiplot(plot_data)
    plt.show()  # This will block until you close the plot window


if __name__ == "__main__":
    # This block runs the two plotting functions sequentially.
    
    # Plot 1: The working example
    plot_br_example()
    
    print("\n###\nPlot 1 (Br) has been closed.\nNow preparing Plot 2 (EPAD Strahl).\n###\n")
    
    # Plot 2: The failing example for debugging
    plot_strahl_example()

    print("\nScript finished.") 