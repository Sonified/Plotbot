#!/usr/bin/env python3
"""
Quick test to verify spectral multiplot fix

REQUIREMENT: This test must be run with conda environment:
conda run -n plotbot_env python test_quick_spectral_fix.py
"""

import sys
import os

# Add the plotbot directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Import necessary plotbot components
from plotbot import epad, multiplot, plt
import matplotlib.pyplot as mpl_plt

def test_quick_spectral():
    """Quick test of spectral multiplot"""
    
    print("🧪 Testing spectral multiplot fix...")
    
    # Enable test printing
    from plotbot.print_manager import print_manager
    print_manager.test_enabled = True
    print_manager.show_status = True
    print_manager.test("[TEST] Test printing enabled for spectral debugging")
    
    # Reset plotting options
    plt.options.reset()
    
    # Configure basic plot options
    plt.options.width = 12
    plt.options.height_per_panel = 4
    plt.options.use_single_title = True
    plt.options.single_title_text = "SPECTRAL FIX TEST: EPAD Strahl"
    
    # Data Selection - 5 panels as requested
    center_times = [
        '2021-01-19/11:30:00.000',
        '2021-01-19/12:00:00.000', 
        '2021-01-19/12:30:00.000',
        '2021-01-19/17:30:00.000',
        '2021-01-19/18:00:00.000'
    ]
    plt.options.window = '00:30:00.000'
    plt.options.position = 'around'
    
    plot_data = [(time, epad.strahl) for time in center_times]
    
    print(f"📊 Creating multiplot with {len(plot_data)} panels...")
    
    # Call Multiplot
    plt.options.show_plot = True  # Display the plot!
    try:
        fig, axs = multiplot(plot_data)
        
        # Check if we have spectral plots
        if not isinstance(axs, list):
            axs = [axs]
            
        spectral_found = False
        for i, ax in enumerate(axs):
            # Check for QuadMesh (pcolormesh) objects
            for child in ax.get_children():
                if hasattr(child, 'get_array') and hasattr(child, 'get_paths'):
                    spectral_found = True
                    print(f"✅ Panel {i+1}: Found spectral plot (QuadMesh)")
                    break
            
            if not spectral_found:
                # Also check for collections which might contain the mesh
                collections = ax.collections
                if collections:
                    spectral_found = True
                    print(f"✅ Panel {i+1}: Found spectral plot (Collections: {len(collections)})")
        
        if spectral_found:
            print("🎉 SUCCESS: Spectral plotting is working!")
            print("📊 Displaying the plot...")
            mpl_plt.show()  # Actually show the plot
            return True
        else:
            print("❌ FAILED: No spectral plots detected")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_quick_spectral()
    if success:
        print("\n✅ Spectral multiplot fix is working!")
    else:
        print("\n❌ Spectral multiplot fix needs more work") 