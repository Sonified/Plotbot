import cdflib
import numpy as np

def check_spectral_data_for_nans():
    """Check existing PSP spectral data for NaN values."""
    
    # Use an existing PSP spectral data file
    file_path = 'data/psp/sweap/spe/l3/spe_af0_pad/2021/psp_swp_spe_af0_L3_pad_20210428_v04.cdf'
    
    print(f"Checking file: {file_path}")
    
    try:
        cdf = cdflib.CDF(file_path)
        
        # List all variables in the file
        variables = cdf.cdf_info()['zVariables']
        print(f"Variables in file: {variables}")
        
        # Look for spectral data variables (typically contain 'EFLUX' or similar)
        spectral_vars = [var for var in variables if 'EFLUX' in var or 'FLUX' in var or 'SPEC' in var]
        print(f"Spectral variables found: {spectral_vars}")
        
        for var in spectral_vars:
            try:
                data = cdf[var][...]
                print(f"\nVariable: {var}")
                print(f"Shape: {data.shape}")
                print(f"Data type: {data.dtype}")
                
                # Check for NaNs
                if np.issubdtype(data.dtype, np.floating):
                    nan_count = np.isnan(data).sum()
                    total_count = data.size
                    nan_percent = (nan_count / total_count) * 100
                    
                    print(f"NaN count: {nan_count:,} out of {total_count:,} ({nan_percent:.2f}%)")
                    
                    if nan_count > 0:
                        print("✅ CONTAINS NANs - This is normal for spectral data")
                    else:
                        print("❌ NO NANs found")
                else:
                    print("Not a floating point array - skipping NaN check")
                    
            except Exception as e:
                print(f"Error reading {var}: {e}")
        
        cdf.close()
        
    except Exception as e:
        print(f"Error opening file: {e}")

if __name__ == "__main__":
    check_spectral_data_for_nans() 