#!/usr/bin/env python3
"""
Example demonstrating vdyes() using the correct Plotbot class-based pattern.

This shows how to use vdyes() exactly like other Plotbot functions:
1. Set parameters on the global instance (like epad.strahl.colorbar_limits = [8, 11])
2. Call function with just trange

RUN INSTRUCTIONS:
This test requires the plotbot_env conda environment:
conda run -n plotbot_env python tests/test_vdyes_plotbot_pattern_example.py

The conda environment includes all required dependencies including bs4 (BeautifulSoup).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from plotbot import *

def test_vdyes_plotbot_pattern():
    """Test vdyes() using the pure Plotbot class-based pattern."""
    
    print('🚀 Setting up VDF parameters on global instance (Plotbot way)...')
    
    # Set parameters on the global instance (like epad.strahl.colorbar_limits = [8, 11])
    psp_span_vdf.theta_x_smart_padding = 150
    psp_span_vdf.phi_y_smart_padding = 150
    psp_span_vdf.enable_smart_padding = True
    psp_span_vdf.enable_zero_clipping = True
    psp_span_vdf.vdf_colormap = 'cool'  # Use the same 'cool' colormap from previous tests
    
    print('✅ Parameters set on global psp_span_vdf instance')
    print(f'   theta_x_smart_padding: {psp_span_vdf.theta_x_smart_padding}')
    print(f'   enable_smart_padding: {psp_span_vdf.enable_smart_padding}')
    print(f'   colormap: {psp_span_vdf.vdf_colormap}')
    
    print('\n🎯 Calling vdyes() with proven working trange...')
    
    # Call with just trange (pure Plotbot pattern)
    trange = ['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000']
    fig = vdyes(trange)
    
    print('🎉 SUCCESS! VDF plot generated using Plotbot class-based system')
    
    # Verify we got a figure back
    assert fig is not None, "vdyes() should return a matplotlib figure"
    print('✅ Test passed - vdyes() works with Plotbot pattern')
    
    # Save the plot so we can see it!
    import os
    save_path = os.path.join('tests', 'Images', 'VDF_vdyes_plotbot_pattern_test.png')
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f'📊 Plot saved to: {save_path}')
    
    # Also show the plot if running interactively
    try:
        import matplotlib.pyplot as plt
        plt.show()
    except:
        pass  # Silent fail if no display available
    
    return fig


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("VDYES() PLOTBOT PATTERN EXAMPLE")
    print("=" * 60)
    
    fig = test_vdyes_plotbot_pattern()
    
    print("\n" + "=" * 60)
    print("EXAMPLE COMPLETE")
    print("This demonstrates the correct Plotbot pattern:")
    print("1. Set parameters on global instance")
    print("2. Call vdyes(trange) - just like plotbot(trange, ...)")
    print("=" * 60)