#!/usr/bin/env python3
"""
Test vdyes() function - single time input for plotbot-style VDF plotting.
This is the streamlined workflow that combines everything we've built.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import numpy as np
import matplotlib.pyplot as plt

# Plotbot imports
from plotbot import vdyes

# vdyes is now imported from plotbot module

def test_vdyes_basic():
    """Test basic vdyes() functionality"""
    print("🧪 Testing vdyes() basic functionality...")
    
    # Test with Jaye's hammerhead example
    timeslice = '2020-01-29/18:10:02.000'
    
    # Test default parameters (smart bounds enabled)
    fig1 = vdyes(timeslice)
    
    # Validate figure structure
    assert len(fig1.axes) == 4, "Should have 4 axes (3 plots + colorbar)"
    
    plt.savefig('tests/Images/vdyes_basic_test.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/vdyes_basic_test.png")
    plt.close(fig1)
    
    print("✅ vdyes() basic test passed!")

def test_vdyes_with_parameters():
    """Test vdyes() with custom parameters"""
    print("🧪 Testing vdyes() with custom parameters...")
    
    timeslice = '2020-01-29/18:10:02.000'
    
    # Test with manual axis limits (disable smart bounds)
    fig2 = vdyes(timeslice,
                  enable_smart_padding=False,
                  theta_x_axis_limits=(-800, 0),
                  theta_y_axis_limits=(-400, 400),
                  phi_x_axis_limits=(-800, 0),
                  phi_y_axis_limits=(-200, 600))
    
    plt.savefig('tests/Images/vdyes_manual_limits_test.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/vdyes_manual_limits_test.png")
    plt.close(fig2)
    
    # Test with custom smart padding
    fig3 = vdyes(timeslice,
                  enable_smart_padding=True,
                  theta_x_smart_padding=50,  # Tighter zoom
                  theta_y_smart_padding=50,
                  phi_x_smart_padding=150,
                  phi_y_smart_padding=150)
    
    plt.savefig('tests/Images/vdyes_custom_padding_test.png', dpi=150, bbox_inches='tight')
    print("✅ Saved: tests/Images/vdyes_custom_padding_test.png")
    plt.close(fig3)
    
    print("✅ vdyes() parameter tests passed!")

if __name__ == "__main__":
    print("🚀 Testing vdyes() - Plotbot-style VDF plotting")
    
    # Run conda environment check
    print("⚠️ Remember to run with: conda run -n plotbot_env python tests/test_VDFine_single_plot.py")
    
    test_vdyes_basic()
    test_vdyes_with_parameters()
    
    print("🎉 All vdyes() tests passed!")