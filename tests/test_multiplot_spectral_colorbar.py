#!/usr/bin/env python3
"""
Test for multiplot spectral colorbar positioning issues.

This test is designed to reproduce and help debug the colorbar positioning
problems mentioned in the multiplot.py code where colorbars "fly way out in the ether".

Run with:
    conda run -n plotbot_anaconda python -m pytest tests/test_multiplot_spectral_colorbar.py -vv -s

Or directly:
    conda run -n plotbot_anaconda python tests/test_multiplot_spectral_colorbar.py
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Add the project root to the path so we can import plotbot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import plotbot components (moved outside functions)
from plotbot import *
from plotbot.multiplot import multiplot
from plotbot.print_manager import print_manager

def test_multiplot_spectral_colorbar_positioning():
    """
    Test that spectral plots in multiplot have properly positioned colorbars.
    
    This test specifically targets the issue where colorbars for spectral plots
    are positioned incorrectly or "fly way out in the ether".
    """
    try:
        
        print("\n" + "="*60)
        print("🔬 TESTING MULTIPLOT SPECTRAL COLORBAR POSITIONING")
        print("="*60)
        
        # Enable debug output for this test
        print_manager.show_debug = True
        print_manager.show_status = True
        
        # Reset options to clean state
        plt.options.reset()
        
        # Configure basic plot options
        plt.options.width = 12
        plt.options.height_per_panel = 4
        plt.options.use_single_title = True
        plt.options.single_title_text = "TEST: Spectral Plot Colorbar Positioning"
        plt.options.constrained_layout = False  # Test with manual layout first
        
        # Test times - use known good data periods
        test_times = [
            '2020-01-29/19:00:00.000',  # Known good PSP data period
            '2020-01-29/20:00:00.000',  # Another test time
        ]
        
        plt.options.window = '02:00:00.000'  # 2 hour window
        plt.options.position = 'around'
        
        # Test with spectral variables that should have colorbars
        spectral_variables = []
        
        # Test EPAD strahl (electron pitch angle spectrogram)
        if hasattr(epad, 'strahl'):
            print("✅ Found epad.strahl - adding to test")
            spectral_variables.append(('epad.strahl', epad.strahl))
        
        # Test proton energy flux if available
        if hasattr(proton, 'energy_flux'):
            print("✅ Found proton.energy_flux - adding to test")
            spectral_variables.append(('proton.energy_flux', proton.energy_flux))
            
        # Test DFB spectral data if available
        if hasattr(psp_dfb, 'ac_spec_dv12'):
            print("✅ Found psp_dfb.ac_spec_dv12 - adding to test")
            spectral_variables.append(('psp_dfb.ac_spec_dv12', psp_dfb.ac_spec_dv12))
        
        if not spectral_variables:
            print("⚠️  No spectral variables found - skipping spectral colorbar test")
            return
            
        # Test each spectral variable
        for var_name, var in spectral_variables:
            print(f"\n🧪 Testing spectral variable: {var_name}")
            print("-" * 40)
            
            # Create plot data for multiplot
            plot_data = [(time, var) for time in test_times]
            
            # Call multiplot and capture any errors
            try:
                print(f"📊 Creating multiplot for {var_name}...")
                fig, axs = multiplot(plot_data)
                
                # Check if colorbars were created properly
                colorbar_found = False
                colorbar_positions = []
                
                # Look for colorbar axes in the figure
                for ax in fig.axes:
                    # Check if this looks like a colorbar axis (typically very narrow)
                    pos = ax.get_position()
                    aspect_ratio = pos.width / pos.height if pos.height > 0 else 0
                    
                    if aspect_ratio < 0.1:  # Very narrow axis, likely a colorbar
                        colorbar_found = True
                        colorbar_positions.append({
                            'x0': pos.x0, 'y0': pos.y0, 
                            'x1': pos.x1, 'y1': pos.y1,
                            'width': pos.width, 'height': pos.height
                        })
                        print(f"🎨 Found colorbar at position: x0={pos.x0:.3f}, y0={pos.y0:.3f}, width={pos.width:.3f}, height={pos.height:.3f}")
                
                if colorbar_found:
                    print(f"✅ {var_name}: Colorbars found and positioned")
                    
                    # Check if colorbars are in reasonable positions
                    for i, cb_pos in enumerate(colorbar_positions):
                        if cb_pos['x0'] > 1.0 or cb_pos['x1'] > 1.2:
                            print(f"❌ Colorbar {i} appears to be positioned too far right (flying in ether)")
                            print(f"   Position: x0={cb_pos['x0']:.3f}, x1={cb_pos['x1']:.3f}")
                        elif cb_pos['x0'] < 0.0:
                            print(f"❌ Colorbar {i} appears to be positioned too far left")
                        else:
                            print(f"✅ Colorbar {i} appears to be reasonably positioned")
                else:
                    print(f"❌ {var_name}: No colorbars found! This might be the issue.")
                
                # Save test plot for manual inspection
                test_filename = f"test_spectral_colorbar_{var_name.replace('.', '_')}.png"
                test_filepath = f"/Users/robertalexander/GitHub/Plotbot/tests/test_logs/{test_filename}"
                
                # Ensure test_logs directory exists
                os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
                
                print(f"💾 Saving test plot to: {test_filepath}")
                fig.savefig(test_filepath, dpi=150, bbox_inches='tight')
                
                plt.close(fig)  # Close to prevent memory issues
                
            except Exception as e:
                print(f"❌ Error testing {var_name}: {str(e)}")
                print(f"   Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("🏁 SPECTRAL COLORBAR TEST COMPLETE")
        print("="*60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in spectral colorbar test: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def test_multiplot_spectral_with_constrained_layout():
    """
    Test spectral plots with constrained_layout=True to see if it fixes colorbar issues.
    """
    try:
        
        print("\n🔬 Testing spectral plots with constrained_layout=True")
        
        # Reset and configure with constrained layout
        plt.options.reset()
        plt.options.constrained_layout = True
        plt.options.width = 12
        plt.options.height_per_panel = 4
        
        # Use a simple test case
        test_times = ['2020-01-29/19:00:00.000']
        plt.options.window = '01:00:00.000'
        plt.options.position = 'around'
        
        if hasattr(epad, 'strahl'):
            plot_data = [(test_times[0], epad.strahl)]
            
            print("📊 Creating multiplot with constrained_layout=True...")
            fig, axs = multiplot(plot_data)
            
            # Save comparison plot
            test_filepath = "/Users/robertalexander/GitHub/Plotbot/tests/test_logs/test_spectral_constrained_layout.png"
            os.makedirs(os.path.dirname(test_filepath), exist_ok=True)
            fig.savefig(test_filepath, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"💾 Saved constrained layout test to: {test_filepath}")
        
    except Exception as e:
        print(f"❌ Error in constrained layout test: {str(e)}")

if __name__ == "__main__":
    # Run the tests directly
    print("🚀 Running multiplot spectral colorbar tests...")
    test_multiplot_spectral_colorbar_positioning()
    test_multiplot_spectral_with_constrained_layout()
    print("✅ Tests complete!")
