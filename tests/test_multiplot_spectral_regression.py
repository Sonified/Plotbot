#!/usr/bin/env python3
"""
Simple, direct test for multiplot spectral regression.
Mirrors the structure of working tests in test_stardust.py.
"""

import sys
import os

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import necessary plotbot components
from plotbot.multiplot import multiplot
from plotbot.multiplot_options import plt
from plotbot.data_cubby import data_cubby
from plotbot.print_manager import print_manager

def test_multiplot_epad_strahl_spectral():
    """
    Tests multiplot with epad.strahl spectral data.
    This test is designed to be simple and directly expose any issues
    with data handling for spectral plots in multiplot.
    """
    
    print("\n================================================================================")
    print("TEST: Multiplot EPAD Strahl Spectral Regression")
    print("================================================================================\n")
    
    try:
        # --- Basic Test Setup ---
        # Enable debug prints to see internal processing
        print_manager.show_debug = True
        print_manager.show_status = True
        
        # Set options to show the plot, not save it.
        plt.options.show_plot = True
        plt.options.save_plot = False
        
        # Configure multiplot windowing
        plt.options.window = '2 hours'
        plt.options.position = 'around'
        plt.options.use_single_title = True
        plt.options.single_title_text = "Multiplot Spectral Test (EPAD Strahl)"
        
        print("--> Test options set. show_plot=True, debug prints enabled.")

        # --- Get Variable ---
        # Get epad_strahl directly from the data_cubby.
        # multiplot is responsible for loading the data for the requested time ranges.
        epad_class = data_cubby.grab('epad')
        epad_strahl = epad_class.get_subclass('strahl')
        
        print(f"--> Grabbed variable '{epad_strahl.subclass_name}' from data_cubby.")

        # --- Create Plot List ---
        plot_list = [
            ('2021-01-19 12:00:00', epad_strahl),
            ('2021-01-19 18:00:00', epad_strahl)
        ]
        
        print(f"--> Created plot list with {len(plot_list)} panels for multiplot.")

        # --- Call Multiplot ---
        # This call should trigger the data loading within multiplot
        print("\n--> Calling multiplot...")
        fig, axs = multiplot(plot_list)
        print("--> Multiplot call completed.")
        
        # --- Verification ---
        print("\n--> Verifying results...")
        assert fig is not None, "Figure object should not be None"
        assert axs is not None, "Axes object should not be None"
        
        spectral_plots_found = 0
        for i, ax in enumerate(axs):
            if len(ax.get_images()) > 0:
                spectral_plots_found += 1
                print(f"    ✅ Panel {i+1}: Found spectral plot (pcolormesh image).")
            else:
                print(f"    ⚠️ Panel {i+1}: No spectral plot found.")
        
        assert spectral_plots_found > 0, "At least one spectral plot should have been created."
        print("--> Verification complete.")
        
    except Exception as e:
        print(f"❌ TEST FAILED: An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_multiplot_epad_strahl_spectral()
    # Keep the plot window open for viewing
    if plt.options.show_plot:
        print("\n--> Displaying plot. Close the plot window to exit the script.")
        plt.show() 