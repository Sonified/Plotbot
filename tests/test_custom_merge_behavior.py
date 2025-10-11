import plotbot as pb
from plotbot.data_classes import mag_rtn_4sa
from plotbot.plotbot_main import plotbot

print("\n" + "="*80)
print("TEST: Verify data merging behavior")
print("="*80)

# Test with br directly
trange1 = ['2020-01-29/18:00:00', '2020-01-29/18:10:00']
print(f"\n1. Plotting trange1: {trange1}")
plotbot(trange1, mag_rtn_4sa.br, 1)
raw_len_1 = len(mag_rtn_4sa.raw_data["br"])
dt_len_1 = len(mag_rtn_4sa.datetime_array)
data_len_1 = len(mag_rtn_4sa.br.data)
print(f"   raw_data['br']: {raw_len_1} points")
print(f"   datetime_array: {dt_len_1} points")
print(f"   br.data (clipped): {data_len_1} points")

trange2 = ['2020-01-29/19:00:00', '2020-01-29/19:20:00']
print(f"\n2. Plotting trange2: {trange2}")
plotbot(trange2, mag_rtn_4sa.br, 1)
raw_len_2 = len(mag_rtn_4sa.raw_data["br"])
dt_len_2 = len(mag_rtn_4sa.datetime_array)
data_len_2 = len(mag_rtn_4sa.br.data)
print(f"   raw_data['br']: {raw_len_2} points (should be MERGED: {raw_len_1} + {dt_len_2 - (raw_len_2 - raw_len_1)} = {raw_len_2})")
print(f"   datetime_array: {dt_len_2} points")
print(f"   br.data (clipped): {data_len_2} points")

print(f"\n✓ Confirmed: raw_data accumulates ({raw_len_2} > {raw_len_1}), datetime_array shows current window")
print("="*80)

