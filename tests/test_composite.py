# Quick test of VDF composite functionality
from plotbot import *
import matplotlib.pyplot as plt

# Test data
trange = ['2023/01/01 12:00:00', '2023/01/01 14:00:00']

print("Testing VDF + plotbot composite...")

# Test the composite functionality
try:
    composite_fig = vdyes(trange, mag_rtn_4sa.br, mag_rtn_4sa.bt)
    print(f"✅ SUCCESS: Composite works! Type: {type(composite_fig)}")
    print(f"Figure size: {composite_fig.get_size_inches()}")
    
    # SHOW the plot!
    plt.show()
    
    # Also save it so you can see it
    composite_fig.savefig('composite_test.png', dpi=150, bbox_inches='tight')
    print("📁 Saved to: composite_test.png")
    print("🎉 VDF + plotbot composite is working!")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
