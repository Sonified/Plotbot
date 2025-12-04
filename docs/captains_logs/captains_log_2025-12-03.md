# Captain's Log - 2025-12-03

## Hammerhead Angular Binning: ±3 Day Analysis with Accurate Perihelion Times

### Summary
Created a complete pipeline for generating hammerhead occurrence rate data binned by Carrington longitude, using accurate perihelion times from our `PERIHELION_TIMES` table and SPICE trajectory data. The system pre-computes all data to JSON for fast visualization.

### Background: Why This Was Needed

**The Problem with Srijan's Original Dates:**
- Srijan's `encounters.py` had **incorrect perihelion dates** (e.g., E8 was April 28, should be April 29)
- His code used ±10 days around perihelion, which was too wide for precise analysis
- We needed ±3 days using our verified `PERIHELION_TIMES` from `plotbot/utils.py`

**Our Accurate Perihelion Times:**
```python
PERIHELION_TIMES = {
    4: '2020/01/29 09:37:00.000', 5: '2020/06/07 08:23:00.000',
    6: '2020/09/27 09:16:00.000', 7: '2021/01/17 17:40:00.000',
    8: '2021/04/29 08:48:00.000', 9: '2021/08/09 19:11:00.000',
    10: '2021/11/21 08:23:00.000', 11: '2022/02/25 15:38:00.000',
    12: '2022/06/01 22:51:00.000', 13: '2022/09/06 06:04:00.000',
    14: '2022/12/11 13:16:00.000', 15: '2023/03/17 20:30:00.000',
    16: '2023/06/22 03:46:00.000', 17: '2023/09/27 23:28:00.000',
    18: '2023/12/29 00:56:00.000', 19: '2024/03/30 02:21:00.000',
    20: '2024/06/30 03:47:00.000', 21: '2024/09/30 05:15:00.000',
    22: '2024/12/24 11:53:00.000', 23: '2025/03/22 22:42:00.000',
}
```

---

### Critical Bug Fixed: 600 Billion Element Array

**The Bug:**
When creating the ±3 day generator script, it was getting **OOM killed (exit code 137)** despite the ±10 day version working fine.

**Root Cause:**
```python
# BROKEN: datetime object → datetime64 at MICROSECOND precision
peri_dt = datetime.strptime(peri_str, '%Y/%m/%d %H:%M:%S.%f')
pday = np.datetime64(peri_dt)  # datetime64[us] - microseconds!
enc_days = np.arange(pday - 3_days, pday + 4_days)
# Result: 7 days × 24h × 60m × 60s × 1,000,000μs = 604,800,000,000 elements!
```

**The Fix:**
```python
# FIXED: Cast to DAY precision before using arange
pday = np.datetime64(peri_dt).astype('datetime64[D]')  # datetime64[D] - days!
enc_days = np.arange(pday - 3_days, pday + 4_days)
# Result: 7 elements (as expected)
```

**Why the ±10 day version worked:** It used just a date string like `'2020-01-29'` which defaults to day precision. Our version used full datetime strings with microseconds.

---

### Files Created

#### 1. `tests/ham_bin_generator_3day.py` - JSON Generator
**Purpose:** Compute hammerhead occurrence rates for all encounters and save to JSON.

**What it does:**
1. Loads SPICE kernels for PSP trajectory
2. For each encounter (E04-E23):
   - Uses our accurate `PERIHELION_TIMES`
   - Loads CDF hammerhead data for ±3 days
   - Gets PSP trajectory from SPICE
   - Transforms to Carrington coordinates
   - Bins trajectory by 1° angular separation
   - Counts hammerhead detections in each bin
   - Calculates occurrence rate (ham_count / all_count)
3. Saves everything to JSON

**Runtime:** ~17 seconds for all 20 encounters

**Output:** `data/psp/ham_angular_bins/ham_bin_data_plus_minus_3_days.json`

#### 2. `tests/ham_bar_chart_3day.py` - Fast Visualization
**Purpose:** Plot bar charts from pre-computed JSON (no recalculation).

**What it does:**
- Reads JSON file
- Creates multi-panel bar chart (one panel per encounter)
- Shows hammerhead occurrence rate vs Carrington longitude
- Displays detection count per encounter

**Runtime:** Sub-second (just reads JSON and plots)

**Output:** `tests/ham_bar_chart_3day_E04-E23.png`

#### 3. `data/psp/ham_angular_bins/ham_bin_data_plus_minus_3_days.json` - Pre-computed Data
**Structure:**
```json
{
  "E04": {
    "n_bins": 50,
    "n_detections": 14427,
    "perihelion": "2020/01/29 09:37:00.000",
    "window_days": 3,
    "bins": [
      {
        "start_lon": 57.617...,
        "end_lon": 58.281...,
        "ham_frac": 1.677...,
        "ham_count": 364,
        "all_count": 216
      },
      ...
    ]
  },
  "E05": { ... },
  ...
}
```

---

### Also Committed (Legacy Files)

These are from earlier work with ±10 day windows:

- `data/psp/ham_angular_bins/ham_bin_data_plus_minus_10_days.json` - ±10 day version (uses Srijan's dates)
- `tests/ham_bar_chart_test.py` - Original ±10 day plotting script
- `tests/ham_bar_chart_E18-E23.png` - ±10 day chart for E18-E23
- `tests/ham_bar_chart_all_encounters.png` - ±10 day chart for all encounters
- `tests/ham_bin_benchmark.py` - Performance benchmarking
- `tests/carrington_binning_comparison.json/.txt` - Comparison files
- `tests/test_carrington_lon_comparison.py` - Comparison tests

---

### Technical Details: The Binning Process

**Angular Binning (from Srijan's approach):**
1. Get PSP trajectory at 5-minute cadence from SPICE
2. Transform to HeliographicCarrington coordinates
3. Walk through trajectory, grouping points where angular separation < 1°
4. Each "bin" represents PSP at roughly the same Carrington longitude
5. Count hammerhead detections that fall within each bin's time range
6. Calculate occurrence rate: `ham_count / (all_count + 1)`

**Why +1 in denominator?** Laplace smoothing to avoid division by zero for bins with no trajectory points.

---

### Key Learnings

1. **numpy datetime64 precision matters!** Always check what precision you're getting when converting from Python datetime objects.

2. **Pre-compute and cache expensive operations.** The SPICE transformations and CDF loading take 17 seconds, but plotting from JSON is instant.

3. **Srijan's perihelion dates were wrong.** Always verify source data against authoritative references.

4. **Debug prints with timestamps save hours.** Adding `[{time.time():.1f}]` prefixes immediately showed where the script was hanging.

---

### Usage

**Regenerate JSON (only needed if source data changes):**
```bash
/opt/anaconda3/bin/python tests/ham_bin_generator_3day.py
```

**Create visualization (fast, from JSON):**
```bash
/opt/anaconda3/bin/python tests/ham_bar_chart_3day.py
```

---

### Next Steps (Future Work)

- Integrate this binning approach with Plotbot's main plotting system
- Add capability to overlay multiple encounters on same Carrington longitude axis
- Consider adding interactive visualization with hover data
- May want to create versions with different window sizes (±1 day, ±5 days, etc.)

---

### Git Information
- **Commits:**
  - `d2fe1ac` - Add ±3 day hammerhead binning data and visualization
  - `0ba9398` - Add remaining ham binning test files and ±10 day data
- **Date:** 2025-12-03
- **Status:** ✅ Successfully pushed to origin/main
