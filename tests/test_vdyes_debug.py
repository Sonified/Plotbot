#!/usr/bin/env python3
"""
Debug VDF Widget Issues

Quick debug test to understand why widgets aren't appearing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def debug_vdyes_time_detection():
    """Debug the time point detection logic"""
    print("🔍 Debugging VDF Time Detection")
    print("=" * 50)
    
    # Test the data download and time detection directly
    import pyspedas
    import cdflib
    import pandas as pd
    from dateutil.parser import parse
    
    print("📡 Testing time range analysis...")
    
    # Test with the same range as notebook
    trange = ['2020/01/29 00:00:00.000', '2020/01/30 00:00:00.000']
    print(f"Testing trange: {trange}")
    
    try:
        # Download VDF data
        VDfile = pyspedas.psp.spi(trange, datatype='spi_sf00_8dx32ex8a', level='l2', 
                                  notplot=True, time_clip=True, downloadonly=True, get_support_data=True)
        
        if not VDfile:
            print("❌ No VDF files downloaded")
            return
            
        print(f"📁 Downloaded: {VDfile[0]}")
        
        # Process data
        dat = cdflib.CDF(VDfile[0])
        epoch_dt64 = cdflib.cdfepoch.to_datetime(dat.varget('Epoch'))
        epoch = pd.to_datetime(epoch_dt64).to_pydatetime().tolist()
        
        # Filter time points to requested trange
        start_dt = parse(trange[0].replace('/', ' '))
        end_dt = parse(trange[1].replace('/', ' '))
        
        time_mask = [(t >= start_dt and t <= end_dt) for t in epoch]
        available_times = [epoch[i] for i, mask in enumerate(time_mask) if mask]
        
        n_time_points = len(available_times)
        
        print(f"📊 RESULTS:")
        print(f"   Total epoch points: {len(epoch)}")
        print(f"   Points in trange: {n_time_points}")
        print(f"   First time: {available_times[0] if available_times else 'None'}")
        print(f"   Last time: {available_times[-1] if available_times else 'None'}")
        
        # Decision logic
        if n_time_points == 0:
            print("🔴 RESULT: Error (no data)")
        elif n_time_points == 1:
            print("🟡 RESULT: Static mode (1 time point)")
        else:
            print(f"🟢 RESULT: Widget mode ({n_time_points} time points)")
            
        return n_time_points
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_widget_imports():
    """Debug widget import capabilities"""
    print("\n🔍 Debugging Widget Imports")
    print("=" * 50)
    
    try:
        from IPython.display import display
        print("✅ IPython.display available")
    except ImportError as e:
        print(f"❌ IPython.display unavailable: {e}")
        
    try:
        import ipywidgets as widgets
        print("✅ ipywidgets available")
        print(f"   Version: {widgets.__version__}")
    except ImportError as e:
        print(f"❌ ipywidgets unavailable: {e}")
        
    try:
        from ipywidgets import IntSlider, Button, HBox, VBox, Output, Layout, Label
        print("✅ All widget components available")
    except ImportError as e:
        print(f"❌ Widget components unavailable: {e}")

def debug_vdyes_call():
    """Debug actual vdyes() call"""
    print("\n🔍 Debugging vdyes() Call")
    print("=" * 50)
    
    try:
        from plotbot import vdyes, psp_span_vdf
        
        # Set some parameters
        psp_span_vdf.enable_smart_padding = True
        psp_span_vdf.vdf_colormap = 'cool'
        
        print("📡 Calling vdyes() with widget-triggering trange...")
        
        # Use smaller range that should still have multiple points
        trange = ['2020/01/29 17:00:00.000', '2020/01/29 19:00:00.000']
        print(f"trange: {trange}")
        
        result = vdyes(trange)
        
        print(f"📊 Result type: {type(result)}")
        
        if hasattr(result, 'savefig'):
            print("🟡 Got matplotlib Figure (static mode)")
        elif hasattr(result, 'children'):
            print("🟢 Got ipywidgets Widget (widget mode)")
            print(f"   Widget children: {len(result.children)}")
        else:
            print("❌ Got unexpected result type")
            
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all debug tests"""
    print("🚀 VDF Widget Debug Suite")
    print("=" * 60)
    
    # Test 1: Time detection logic
    n_points = debug_vdyes_time_detection()
    
    # Test 2: Widget imports
    debug_widget_imports()
    
    # Test 3: Actual vdyes call
    result = debug_vdyes_call()
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG SUMMARY")
    print(f"Time points found: {n_points}")
    print(f"Result type: {type(result) if result else 'None'}")
    
    if n_points and n_points > 1:
        if hasattr(result, 'children'):
            print("✅ Everything working correctly - widget mode active")
        else:
            print("❌ Widget mode should activate but didn't - check fallback logic")
    else:
        print("🔍 Check data availability in time range")

if __name__ == "__main__":
    main()