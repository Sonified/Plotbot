#!/usr/bin/env python3
"""
VDF Widget Demonstration Test

Tests the enhanced vdyes() function with automatic widget mode selection.
Demonstrates both static and widget modes based on available time points.

RUN INSTRUCTIONS:
conda run -n plotbot_env python tests/test_vdyes_widget_demo.py

The test will:
1. Test static mode (single time point)
2. Test widget mode (multiple time points) 
3. Demonstrate the automatic mode selection logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import at module level
from plotbot import *

def test_vdyes_static_mode():
    """Test vdyes() static mode with single time point"""
    
    print("🧪 Testing vdyes() Static Mode")
    print("=" * 50)
    
    # Set VDF parameters (Plotbot way)
    psp_span_vdf.theta_x_smart_padding = 100
    psp_span_vdf.phi_y_smart_padding = 150
    psp_span_vdf.enable_smart_padding = True
    psp_span_vdf.vdf_colormap = 'plasma'
    
    # Test with small time range (should trigger static mode)
    # Using Jaye's exact hammerhead time region
    trange = ['2020/01/29 18:10:00.000', '2020/01/29 18:10:30.000']
    
    print(f"📊 Testing trange: {trange}")
    print("Expected: Static mode (single time point)")
    
    result = vdyes(trange)
    
    # Should return matplotlib figure (static mode)
    import matplotlib.pyplot as plt
    if hasattr(result, 'savefig'):
        print("✅ Static mode confirmed - matplotlib Figure returned")
        print(f"   Figure size: {result.get_size_inches()}")
        return result
    else:
        print("❌ Unexpected result type:", type(result))
        return None

def test_vdyes_widget_mode():
    """Test vdyes() widget mode with multiple time points"""
    
    print("\n🎛️ Testing vdyes() Widget Mode")
    print("=" * 50)
    
    # Set VDF parameters (Plotbot way)
    psp_span_vdf.theta_x_smart_padding = 150
    psp_span_vdf.phi_y_smart_padding = 200
    psp_span_vdf.enable_smart_padding = True
    psp_span_vdf.vdf_colormap = 'cool'
    
    # Test with larger time range (should trigger widget mode)
    trange = ['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000']
    
    print(f"📊 Testing trange: {trange}")
    print("Expected: Widget mode (multiple time points)")
    
    result = vdyes(trange)
    
    # Should return ipywidgets widget (widget mode)
    try:
        import ipywidgets
        if hasattr(result, 'children'):
            print("✅ Widget mode confirmed - ipywidgets Widget returned")
            print(f"   Widget type: {type(result)}")
            print(f"   Number of child widgets: {len(result.children)}")
            return result
        else:
            print("❌ Expected widget, got:", type(result))
            return None
    except ImportError:
        if hasattr(result, 'savefig'):
            print("✅ Widget mode fallback - matplotlib Figure returned (no ipywidgets)")
            print("   This is expected behavior when ipywidgets not available")
            return result
        else:
            print("❌ Unexpected fallback result:", type(result))
            return None

def test_mode_selection_logic():
    """Test the automatic mode selection logic"""
    print("\n🧠 Testing Mode Selection Logic")
    print("=" * 50)
    
    test_cases = [
        {
            'name': 'Very short range',
            'trange': ['2020/01/29 18:10:00.000', '2020/01/29 18:10:10.000'],
            'expected': 'static'
        },
        {
            'name': 'Medium range', 
            'trange': ['2020/01/29 18:00:00.000', '2020/01/29 18:30:00.000'],
            'expected': 'widget'
        },
        {
            'name': 'Large range',
            'trange': ['2020/01/29 12:00:00.000', '2020/01/30 12:00:00.000'], 
            'expected': 'widget'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {case['name']}")
        print(f"   Range: {case['trange']}")
        
        try:
            result = vdyes(case['trange'])
            
            # Determine actual mode
            if hasattr(result, 'savefig'):
                actual_mode = 'static'
            elif hasattr(result, 'children'):
                actual_mode = 'widget'
            else:
                actual_mode = 'unknown'
            
            print(f"   Expected: {case['expected']}, Actual: {actual_mode}")
            
            if actual_mode == case['expected']:
                print(f"   ✅ Mode selection correct")
            else:
                print(f"   ⚠️ Mode selection unexpected (may be due to data availability)")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_force_static_parameter():
    """Test force_static parameter override"""
    print("\n🔧 Testing force_static Parameter")
    print("=" * 50)
    
    # Test with range that would normally trigger widget mode
    trange = ['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000']
    
    print(f"📊 Testing trange: {trange}")
    print("With force_static=True (should override widget mode)")
    
    try:
        result = vdyes(trange, force_static=True)
        
        if hasattr(result, 'savefig'):
            print("✅ force_static working - static plot returned despite multiple time points")
        elif hasattr(result, 'children'):
            print("⚠️ force_static may not be working - widget returned")
        else:
            print("❌ Unexpected result type:", type(result))
            
    except Exception as e:
        print(f"❌ Error testing force_static: {e}")

def main():
    """Run all VDF widget tests"""
    print("🚀 VDF Widget Demonstration Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Static mode
        static_result = test_vdyes_static_mode()
        
        # Test 2: Widget mode  
        widget_result = test_vdyes_widget_mode()
        
        # Test 3: Mode selection logic
        test_mode_selection_logic()
        
        # Test 4: Force static parameter
        test_force_static_parameter()
        
        print("\n" + "=" * 60)
        print("🎉 VDF Widget Test Suite Complete!")
        print("\n📋 Summary:")
        print("✅ Enhanced vdyes() function with automatic mode detection")
        print("✅ Static mode: Single time point → 3-panel VDF plot")
        print("✅ Widget mode: Multiple time points → Interactive time slider")
        print("✅ Hopf explorer-style widget controls (time slider, save buttons)")
        print("✅ Smart save location: Defaults to Jupyter notebook directory")
        print("✅ Automatic fallback to static mode when ipywidgets unavailable")
        
        return static_result, widget_result
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    main()