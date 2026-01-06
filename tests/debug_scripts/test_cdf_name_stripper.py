#!/usr/bin/env python3
import re

def smart_strip_cdf_name(filename):
    """
    Ultra-smart CDF filename stripper that handles NASA/ESA/custom conventions.
    """
    # Remove extension
    name = filename.replace('.cdf', '').replace('.CDF', '')
    original = name
    
    # Define aggressive patterns (order matters!)
    patterns = [
        # ISO timestamps: YYYYMMDDHHMMSS (14 digits)
        (r'_\d{14}(?=_|$)', ''),
        # ISO timestamps: YYYYMMDDHHMM (12 digits)
        (r'_\d{12}(?=_|$)', ''),
        # Date+Time: YYYYMMDD_HHMMSS
        (r'_\d{8}_\d{6}(?=_|$)', ''),
        # Date+Time: YYYYMMDD_HHMM
        (r'_\d{8}_\d{4}(?=_|$)', ''),
        # ISO date with dashes: YYYY-MM-DD
        (r'_\d{4}-\d{2}-\d{2}', ''),
        # Compact date: YYYYMMDD (8 digits, not part of longer number)
        (r'(?<![\d])_\d{8}(?=_|$)', ''),
        # Day-of-year: YYYY_DDD or YYYYDDD
        (r'_?\d{4}_\d{3}(?=_|$)', ''),
        (r'(?<![\d])\d{7}(?=_|$)', ''),  # YYYYDDD as 7 digits
        # Year only at end: _YYYY
        (r'_\d{4}(?=_v|\.cdf|$)', ''),
        # Time patterns: HHMMSS, HHMM (be careful - must be 4 or 6 digits before version)
        (r'_\d{6}(?=_v)', ''),  # HHMMSS before version
        (r'_\d{4}(?=_v)', ''),  # HHMM before version
        # Version patterns (very specific to avoid false matches)
        (r'_v\d+\.\d+\.\d+$', ''),  # v1.2.3 at end
        (r'_v\d+\.\d+$', ''),       # v1.2 at end
        (r'_v\d{2,3}$', ''),        # v01, v001 at end
        (r'_version\d+$', ''),      # version1
        # Sequential numbering at very end
        (r'_\d{3}$', ''),  # _001
        (r'_\d{2}$', ''),  # _01
    ]
    
    # Apply patterns
    for pattern, replacement in patterns:
        name = re.sub(pattern, replacement, name)
    
    # Clean up artifacts
    name = re.sub(r'_+', '_', name)  # Multiple underscores
    name = re.sub(r'-+', '-', name)  # Multiple dashes
    name = name.strip('_-')           # Leading/trailing
    
    # Convert to valid Python identifier
    name = name.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)  # Replace invalid chars
    name = re.sub(r'_+', '_', name)          # Clean up again
    
    return name

# Comprehensive test suite
test_files = [
    # PSP
    'psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20210807_v02.cdf',
    'psp_fld_l2_dfb_dc_spec_dv12hg_20211125_v01.cdf',
    
    # WIND
    'wi_elpd_3dp_20220602_v02.cdf',
    'wi_h5_swe_00000000_v01.cdf',
    'wi_h1_swe_20220101_v03.cdf',
    
    # MMS (the problematic one!)
    'mms1_fpi_brst_l2_des-moms_20170802120000_v3.3.0.cdf',
    'mms2_edp_srvy_l2_scpot_20220315000000_v2.4.5.cdf',
    
    # Custom/weird formats
    'PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf',
    'custom_data_file.cdf',
    'psp_data_2021_123_v1.cdf',
    'maven_lpw_l2_lpnt_20210401_v02.cdf',
    'solo_l2_mag-rtn_20200615_v01.cdf',
    
    # Edge cases
    'data_2021123_v01.cdf',  # No underscores
    'test_20210101_20210102_v1.cdf',  # Two dates
]

print("CDF Filename Stripping Test")
print("="*85)
for f in test_files:
    result = smart_strip_cdf_name(f)
    print(f"{f:65s} → {result}")
