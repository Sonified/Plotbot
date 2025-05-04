import numpy as np
import os
import time

def test_simple_class_update():
    """Test that directly demonstrates the issue with class update from Zarr"""
    # 1. Create mock imported_data that mimics what comes from Zarr
    class MockImportedData:
        def __init__(self):
            # Create time array using TT2000 format
            import cdflib
            self.times = cdflib.cdfepoch.compute_tt2000(
                [[2023, 5, 1, 12, 0, 0, 0], [2023, 5, 1, 12, 30, 0, 0]])
            
            # Create field data that has the right structure
            self.data = {
                'psp_fld_l2_mag_RTN_4_Sa_per_Cyc': np.array([[1, 2, 3], [4, 5, 6]])
            }
    
    # 2. Get the actual class and update it
    mock_data = MockImportedData()
    from plotbot.data_classes.psp_mag_classes import mag_rtn_4sa
    
    # Add extensive debug in calculate_variables to see what's failing
    mag_rtn_4sa.update(mock_data)
    
    # 3. Verify datetime_array is set correctly
    assert mag_rtn_4sa.datetime_array is not None


def test_epad_plot_manager_after_get_data():
    """Test to inspect epad.strahl after running get_data."""
    from plotbot.get_data import get_data
    from plotbot.data_classes.psp_electron_classes import epad
    # Use a short, valid trange for which data should exist
    trange = ['2021/04/26 00:00:00.000', '2021/04/26 06:00:00.000']
    get_data(trange, epad.strahl)
    # Now inspect the plot_manager object
    strahl_pm = epad.strahl
    print(f"epad.strahl type: {type(strahl_pm)}")
    if hasattr(strahl_pm, 'shape'):
        print(f"epad.strahl shape: {strahl_pm.shape}")
    if hasattr(strahl_pm, 'plot_options'):
        print(f"epad.strahl plot_options: {strahl_pm.plot_options}")
    if hasattr(strahl_pm, 'dims'):
        print(f"epad.strahl dims: {strahl_pm.dims}")
    if hasattr(strahl_pm, 'data'):
        print(f"epad.strahl data shape: {np.shape(strahl_pm.data)}")


def test_load_pad_cdf():
    """Test loading a PAD CDF file and inspecting its variables and data."""
    from cdflib import CDF
    cdf_path = "psp_data/sweap/spe/l3/spe_af0_pad/2018/psp_swp_spe_af0_L3_pad_20181026_v04.cdf"
    import os
    if not os.path.isfile(cdf_path):
        print(f"❌ PAD CDF file not found: {cdf_path}")
        return
    try:
        with CDF(cdf_path) as cdf:
            variables = cdf.cdf_info().zVariables
            print(f"Variables in CDF: {variables}")
            # Try to find a likely PAD variable
            possible_names = [
                'EFLUX_VS_PA_E', 'PAD', 'psp_swp_spe_af0_L3_pad', 'EFLUX', 'EFLUX_PAD'
            ]
            var_name = next((v for v in possible_names if v in variables), None)
            if not var_name:
                print(f"Could not find expected PAD variable in {cdf_path}")
                return
            data = cdf.varget(var_name)
            print(f"{var_name} shape: {data.shape}")
            print(f"First 5 rows (flattened):\n{data.reshape(-1, data.shape[-1])[:5]}")
            print("✅ PAD CDF load test passed.")
    except Exception as e:
        print(f"❌ PAD CDF load test failed: {e}")


def test_inspect_all_captains_log_cdf_files():
    """Open each CDF file listed in the captain's log and print variable structure, using psp_data_types.py for context."""
    import os
    from cdflib import CDF
    from plotbot.data_classes.psp_data_types import data_types

    # List of (data_type, file_path) tuples, with relative paths
    files = [
        ('mag_RTN', 'psp_data/fields/l2/mag_rtn/2020/psp_fld_l2_mag_RTN_2020040906_v02.cdf'),
        ('mag_RTN_4sa', 'psp_data/fields/l2/mag_rtn_4_per_cycle/2018/psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20181017_v02.cdf'),
        ('mag_sc', 'psp_data/fields/l2/mag_sc/2021/psp_fld_l2_mag_SC_2021042600_v02.cdf'),
        ('mag_sc_4sa', 'psp_data/fields/l2/mag_sc_4_per_cycle/2020/psp_fld_l2_mag_sc_4_sa_per_cyc_20200409_v02.cdf'),
        ('spe_af0_pad', 'psp_data/sweap/spe/l3/spe_af0_pad/2018/psp_swp_spe_af0_L3_pad_20181026_v04.cdf'),
        ('spe_sf0_pad', 'psp_data/sweap/spe/l3/spe_sf0_pad/2018/psp_swp_spe_sf0_L3_pad_20181017_v04.cdf'),
        ('spi_sf00_l3_mom', 'psp_data/sweap/spi/l3/spi_sf00_l3_mom/2018/psp_swp_spi_sf00_L3_mom_20181104_v04.cdf'),
    ]

    for data_type, cdf_path in files:
        print(f"\n=== {data_type} ===")
        print(f"File: {cdf_path}")
        if not os.path.isfile(cdf_path):
            print(f"❌ File not found: {cdf_path}")
            continue
        try:
            with CDF(cdf_path) as cdf:
                variables = cdf.cdf_info().zVariables
                print(f"Variables: {variables}")
                # Get expected var_dims from psp_data_types.py
                var_dims = data_types.get(data_type, {}).get('var_dims', {})
                for var in variables:
                    data = cdf.varget(var)
                    print(f"- {var}: shape={np.shape(data)}, dtype={data.dtype if hasattr(data, 'dtype') else type(data)}")
                    if var in var_dims:
                        print(f"  Expected dims: {var_dims[var]}")
                    # Print a preview of the data
                    try:
                        preview = data
                        if hasattr(data, 'shape') and data.shape and data.size > 0:
                            if data.ndim == 1:
                                preview = data[:5]
                            elif data.ndim == 2:
                                preview = data[:5, :5]
                            elif data.ndim == 3:
                                preview = data[:2, :2, :2]
                            else:
                                preview = data.flat[:5]
                        print(f"  Preview: {preview}")
                    except Exception as e:
                        print(f"  Could not preview data: {e}")
                    # Print variable attributes if available
                    try:
                        attrs = cdf.varattsget(var)
                        if attrs:
                            print(f"  Attributes: {attrs}")
                    except Exception as e:
                        print(f"  Could not get attributes: {e}")
        except Exception as e:
            print(f"❌ Failed to open or inspect {cdf_path}: {e}")


def test_plot_manager_structure_from_epad():
    """Test to inspect all plot_manager objects in epad and print their structural metadata."""
    from plotbot.data_classes.psp_electron_classes import epad
    # Ensure data is loaded (simulate a get_data call if needed)
    # For this test, we assume epad has already been updated with data
    for attr in dir(epad):
        obj = getattr(epad, attr)
        if hasattr(obj, 'plot_options'):
            print(f"\n--- {attr} ---")
            po = obj.plot_options
            print(f"plot_type: {getattr(po, 'plot_type', None)}")
            print(f"shape: {getattr(obj, 'shape', np.shape(getattr(obj, 'data', [])))}")
            print(f"dims: {getattr(obj, 'dims', None)}")
            print(f"y_label: {getattr(po, 'y_label', None)}")
            print(f"additional_data: {getattr(po, 'additional_data', None)}")
            # Print axis labels if available
            if hasattr(po, 'legend_label'):
                print(f"legend_label: {po.legend_label}")
            if hasattr(po, 'colormap'):
                print(f"colormap: {po.colormap}")
            if hasattr(po, 'colorbar_scale'):
                print(f"colorbar_scale: {po.colorbar_scale}")


def test_get_and_inspect_epad_strahl():
    """Test loading epad.strahl with get_data and inspecting its structure."""
    from plotbot.get_data import get_data
    from plotbot.data_classes.psp_electron_classes import epad
    trange = ['2022/02/25 12:00:00.000', '2022/02/25 13:00:00.000']
    get_data(trange, epad.strahl)
    strahl_pm = epad.strahl
    print(f"epad.strahl type: {type(strahl_pm)}")
    if hasattr(strahl_pm, 'shape'):
        print(f"epad.strahl shape: {strahl_pm.shape}")
    if hasattr(strahl_pm, 'plot_options'):
        print(f"epad.strahl plot_options: {strahl_pm.plot_options}")
    if hasattr(strahl_pm, 'dims'):
        print(f"epad.strahl dims: {strahl_pm.dims}")
    if hasattr(strahl_pm, 'data'):
        print(f"epad.strahl data shape: {np.shape(strahl_pm.data)}")


def test_profile_zarr_vs_cdf_load():
    """Profile time to load epad.strahl from CDF (no Zarr) vs. from Zarr, and print speedup factor. Also print data preview after Zarr import."""
    from plotbot.get_data import get_data
    from plotbot.data_classes.psp_electron_classes import epad
    zarr_path = 'data_cubby/spe_sf0_pad/2022/02/25.zarr'
    # Ensure Zarr file is deleted
    if os.path.exists(zarr_path):
        import shutil
        shutil.rmtree(zarr_path)
        print(f"Deleted Zarr file: {zarr_path}")
    trange = ['2022/02/25 12:00:00.000', '2022/02/25 13:00:00.000']
    # Profile CDF import
    t0 = time.time()
    get_data(trange, epad.strahl)
    t1 = time.time()
    cdf_duration = t1 - t0
    print(f"CDF import and calculation duration: {cdf_duration:.6f} seconds")
    # Profile Zarr import
    t2 = time.time()
    get_data(trange, epad.strahl)
    t3 = time.time()
    zarr_duration = t3 - t2
    print(f"Zarr import duration: {zarr_duration:.6f} seconds")
    if zarr_duration > 0:
        speedup = cdf_duration / zarr_duration
        print(f"Zarr is {speedup:.2f}x faster than CDF import.")
    else:
        print("Zarr duration was too fast to measure!")
    # Print data preview after Zarr import
    strahl_pm = epad.strahl
    print(f"epad.strahl type: {type(strahl_pm)}")
    if hasattr(strahl_pm, 'shape'):
        print(f"epad.strahl shape: {strahl_pm.shape}")
    if hasattr(strahl_pm, 'data'):
        print(f"epad.strahl data shape: {np.shape(strahl_pm.data)}")
        print(f"epad.strahl data preview: {strahl_pm.data[:5, :5]}")


def test_profile_zarr_vs_cdf_load_mag_rtn():
    """Profile time to load mag_rtn.br from CDF (no Zarr) vs. from Zarr, and print speedup factor and data preview."""
    from plotbot.get_data import get_data
    from plotbot.data_classes.psp_mag_classes import mag_rtn
    zarr_path = 'data_cubby/mag_rtn/2020/04/09.zarr'
    # Ensure Zarr file is deleted
    if os.path.exists(zarr_path):
        import shutil
        shutil.rmtree(zarr_path)
        print(f"Deleted Zarr file: {zarr_path}")
    # Use a 6-hour range in the middle of the day
    trange = ['2020/04/09 09:00:00.000', '2020/04/09 15:00:00.000']
    # Profile CDF import
    t0 = time.time()
    get_data(trange, mag_rtn.br)
    t1 = time.time()
    cdf_duration = t1 - t0
    print(f"CDF import and calculation duration: {cdf_duration:.6f} seconds")
    # Profile Zarr import
    t2 = time.time()
    get_data(trange, mag_rtn.br)
    t3 = time.time()
    zarr_duration = t3 - t2
    print(f"Zarr import duration: {zarr_duration:.6f} seconds")
    if zarr_duration > 0:
        speedup = cdf_duration / zarr_duration
        print(f"Zarr is {speedup:.2f}x faster than CDF import.")
    else:
        print("Zarr duration was too fast to measure!")
    # Print data preview after Zarr import
    br_pm = mag_rtn.br
    print(f"mag_rtn.br type: {type(br_pm)}")
    if hasattr(br_pm, 'shape'):
        print(f"mag_rtn.br shape: {br_pm.shape}")
    if hasattr(br_pm, 'data'):
        print(f"mag_rtn.br data shape: {np.shape(br_pm.data)}")
        print(f"mag_rtn.br data preview: {br_pm.data[:5]}")


def test_plotbot_end_to_end_mag_and_epad():
    """Test full plotbot workflow: import plotbot as pb, call pb.plotbot with mag_rtn_4sa.br and epad.strahl."""
    import plotbot as pb
    test_range = ['2022/04/14 00:00:00.000', '2022/04/14 06:00:00.000']
    print("[TEST] Calling pb.plotbot with mag_rtn_4sa.br and epad.strahl...")
    pb.plotbot(test_range, pb.mag_rtn_4sa.br, 1, pb.epad.strahl, 2)
    print("[TEST] pb.plotbot call complete.") 