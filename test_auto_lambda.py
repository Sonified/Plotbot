import numpy as np
import plotbot

# Sam's exact syntax - should auto-convert to lambda
phi_B = plotbot.custom_variable('phi_B', 
    np.degrees(np.arctan2(plotbot.mag_rtn_4sa.br, plotbot.mag_rtn_4sa.bn)) + 180
)

print("phi_B created!")
print(f"phi_B shape: {phi_B.shape}")

# Load data
trange = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
plotbot.plotbot(trange, plotbot.mag_rtn_4sa.br, 1, plotbot.phi_B, 2)

# Check result
br = np.array(plotbot.mag_rtn_4sa.br.data)
bn = np.array(plotbot.mag_rtn_4sa.bn.data)
phi_B_data = np.array(plotbot.phi_B.data)

print(f"\nbr shape: {br.shape}")
print(f"phi_B shape: {phi_B_data.shape}")

if len(phi_B_data) > 0:
    expected = np.degrees(np.arctan2(br[0], bn[0])) + 180
    print(f"\nphi_B[0]: {phi_B_data[0]:.6f}")
    print(f"Expected: {expected:.6f}")
    if np.isclose(phi_B_data[0], expected):
        print("✅ AUTO-LAMBDA WORKS!")
    else:
        print("❌ Values don't match")
else:
    print("❌ phi_B is empty!")


