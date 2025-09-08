#!/usr/bin/env python3
# test_plotbot_interactive.py
# To run tests from the project root directory and see print output in the console:
# conda run -n plotbot_env python test_plotbot_interactive.py -v
# To run a specific test function and see print output:
# conda run -n plotbot_env python -c "from test_plotbot_interactive import test_simple_interactive; test_simple_interactive()"
# The script includes detailed output for debugging interactive functionality.

"""
Simple test script for plotbot_interactive() function

Tests the new interactive plotting functionality with click-to-VDF capabilities
while maintaining publication-ready styling that matches Plotbot's matplotlib aesthetic.
"""

# Test the import
try:
    import plotbot
    from plotbot import plotbot_interactive
    print("✅ Import successful!")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test a simple interactive plot
def test_simple_interactive():
    """Test basic interactive functionality"""
    try:
        # Define a simple time range
        trange = ['2020-01-29/17:00:00.000', '2020-01-29/19:00:00.000']
        
        print("🚀 Testing plotbot_interactive...")
        print(f"   Time range: {trange}")
        
        # Test with matplotlib fallback first (safer)
        print("\n📈 Testing matplotlib fallback...")
        result = plotbot_interactive(trange, 
                                   plotbot.mag_rtn_4sa.br, 1,
                                   backend='matplotlib')
        
        if result:
            print("✅ Matplotlib fallback works!")
        else:
            print("⚠️ Matplotlib fallback had issues")
        
        # Test interactive mode (if dependencies available)
        print("\n🎛️ Testing interactive mode...")
        app = plotbot_interactive(trange, 
                                plotbot.mag_rtn_4sa.br, 1,
                                plotbot.mag_rtn_4sa.bt, 1,
                                port=8051)  # Use different port
        
        if app:
            print("✅ Interactive mode created successfully!")
            print("🌐 Check your browser at: http://127.0.0.1:8051")
            print("📌 Click on data points to test VDF functionality")
            return True
        else:
            print("⚠️ Interactive mode fell back to matplotlib")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 plotbot_interactive() Test Script")
    print("=" * 50)
    
    success = test_simple_interactive()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("📝 Next steps:")
        print("   1. Check the browser for the interactive plot")
        print("   2. Click on data points to test VDF generation")
        print("   3. Try the example notebook for more features")
    else:
        print("\n❌ Test had issues - check error messages above")
