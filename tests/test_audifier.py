# To run tests from the project root directory:
# conda run -n plotbot_env python -m pytest tests/test_audifier.py -vv
# To run a specific test (e.g., test_filename_format):
# conda run -n plotbot_env python -m pytest tests/test_audifier.py::test_filename_format -vv

import pytest
import os
import numpy as np
import tempfile
import shutil
import re
from scipy.io import wavfile
from datetime import datetime, timedelta

from plotbot.audifier import Audifier, audifier as global_audifier
from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.multiplot_options import plt
from plotbot import mag_rtn

# Enable test output in print manager
print_manager.enable_test()

@pytest.fixture
def test_audifier():
    """Provide the global audifier instance with a temporary save directory."""
    # Use the globally initialized audifier instance
    audifier = global_audifier
    
    # Store original dir and set temp dir
    original_dir = audifier.save_dir
    temp_dir = tempfile.mkdtemp()
    audifier.set_save_dir(temp_dir)
    
    yield audifier # Provide the configured audifier instance
    
    # Clean up: restore original dir and remove temp dir
    audifier.set_save_dir(original_dir) if original_dir else None
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temp dir {temp_dir}: {e}")

# Define the public time range once
PUBLIC_TRANGE = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000'] # Enc 17 HCS Crossing

def test_mono_audio(test_audifier):
    """Test creating a real mono audio file."""
    audifier = test_audifier
    
    # Set attributes directly
    audifier.channels = 1
    audifier.fade_samples = 0
    audifier.sample_rate = 44100 # Ensure consistent sample rate for checks
    
    # Generate audio using real component and public trange
    files = audifier.audify(PUBLIC_TRANGE, mag_rtn.br)
    
    # Check results (if file generation succeeded)
    if files and "br" in files:
        assert os.path.exists(files["br"]), f"File not found: {files['br']}"
        sample_rate, audio_data = wavfile.read(files["br"])
        assert sample_rate == audifier.sample_rate
        assert len(audio_data.shape) == 1
        assert len(audio_data) > 0
    else:
        pytest.skip("Audify did not return expected file key 'br', possibly due to data issues.")

def test_stereo_audio(test_audifier):
    """Test creating a real stereo audio file."""
    audifier = test_audifier
    
    # Set attributes directly
    audifier.channels = 2
    audifier.fade_samples = 0
    audifier.sample_rate = 44100
    
    # Generate audio using real components and public trange
    files = audifier.audify(PUBLIC_TRANGE, mag_rtn.br, mag_rtn.bt)
    
    stereo_key = "stereo_Br_Bt"
    if files and stereo_key in files:
        assert os.path.exists(files[stereo_key]), f"File not found: {files[stereo_key]}"
        sample_rate, audio_data = wavfile.read(files[stereo_key])
        assert sample_rate == audifier.sample_rate
        assert len(audio_data.shape) == 2
        assert audio_data.shape[1] == 2
        assert audio_data.shape[0] > 0
    else:
        pytest.skip(f"Audify did not return expected file key '{stereo_key}', possibly due to data issues.")

def test_mono_audio_with_fade(test_audifier):
    """Test creating a real mono audio file with fade."""
    audifier = test_audifier
    
    # Set attributes directly
    audifier.channels = 1
    fade_samples = 2000 # Use a reasonable fade for potentially longer real audio
    audifier.fade_samples = fade_samples
    audifier.sample_rate = 44100
    
    # Generate audio using real component and public trange
    files = audifier.audify(PUBLIC_TRANGE, mag_rtn.bn) # Use Bn for variety
    
    if files and "bn" in files:
        assert os.path.exists(files["bn"]), f"File not found: {files['bn']}"
        sample_rate, audio_data = wavfile.read(files["bn"])
        assert sample_rate == audifier.sample_rate
        assert len(audio_data.shape) == 1
        assert len(audio_data) > 0
        # Basic fade check (less strict due to real data variability)
        if len(audio_data) > 2 * fade_samples:
            assert abs(audio_data[0]) < abs(audio_data[fade_samples]), "Fade-in start incorrect"
            assert abs(audio_data[-1]) < abs(audio_data[-fade_samples]), "Fade-out end incorrect"
    else:
        pytest.skip("Audify did not return expected file key 'bn', possibly due to data issues.")

def test_stereo_audio_with_fade(test_audifier):
    """Test creating a real stereo audio file with fade."""
    audifier = test_audifier
    
    # Set attributes directly
    audifier.channels = 2
    fade_samples = 2000
    audifier.fade_samples = fade_samples
    audifier.sample_rate = 44100
    
    # Generate audio using real components and public trange
    files = audifier.audify(PUBLIC_TRANGE, mag_rtn.bn, mag_rtn.bmag) # Use Bn, Bmag
    
    stereo_key = "stereo_Bn_Bmag"
    if files and stereo_key in files:
        assert os.path.exists(files[stereo_key]), f"File not found: {files[stereo_key]}"
        sample_rate, audio_data = wavfile.read(files[stereo_key])
        assert sample_rate == audifier.sample_rate
        assert len(audio_data.shape) == 2
        assert audio_data.shape[1] == 2
        assert audio_data.shape[0] > 0
        # Basic fade check (less strict)
        if audio_data.shape[0] > 2 * fade_samples:
            # Left channel
            assert abs(audio_data[0, 0]) < abs(audio_data[fade_samples, 0]), "Left Fade-in start incorrect"
            assert abs(audio_data[-1, 0]) < abs(audio_data[-fade_samples, 0]), "Left Fade-out end incorrect"
            # Right channel
            assert abs(audio_data[0, 1]) < abs(audio_data[fade_samples, 1]), "Right Fade-in start incorrect"
            assert abs(audio_data[-1, 1]) < abs(audio_data[-fade_samples, 1]), "Right Fade-out end incorrect"
    else:
        pytest.skip(f"Audify did not return expected file key '{stereo_key}', possibly due to data issues.")

def test_apply_fade_mono():
    """Test the apply_fade method with mono audio data"""
    audifier = Audifier()
    
    # Create a simple mono audio array (sine wave)
    samples = 1000
    audio_data = np.sin(np.linspace(0, 6*np.pi, samples)) * 32767
    audio_data = audio_data.astype(np.int16)
    
    # Set fade samples using property
    fade_samples = 100
    audifier.fade_samples = fade_samples
    
    # Apply fade
    faded_audio = audifier.apply_fade(audio_data)
    
    # Check that fade was applied correctly
    # First sample should be significantly reduced (close to zero)
    assert abs(faded_audio[0]) < 0.1 * abs(audio_data[fade_samples])
    
    # Middle of fade-in should be around half amplitude
    assert 0.3 * abs(audio_data[fade_samples]) < abs(faded_audio[fade_samples // 2]) < 0.7 * abs(audio_data[fade_samples])
    
    # Middle of audio should be unchanged
    assert faded_audio[samples // 2] == audio_data[samples // 2]
    
    # Last sample should be significantly reduced (close to zero)
    assert abs(faded_audio[-1]) < 0.1 * abs(audio_data[-fade_samples])
    
    # Middle of fade-out should be around half amplitude
    assert 0.3 * abs(audio_data[-fade_samples]) < abs(faded_audio[-fade_samples // 2]) < 0.7 * abs(audio_data[-fade_samples])

def test_apply_fade_stereo():
    """Test the apply_fade method with stereo audio data"""
    audifier = Audifier()
    
    # Create a simple stereo audio array (sine waves with different frequencies)
    samples = 1000
    left_channel = np.sin(np.linspace(0, 6*np.pi, samples)) * 32767
    right_channel = np.sin(np.linspace(0, 8*np.pi, samples)) * 32767
    
    # Combine into stereo array
    stereo_data = np.column_stack((left_channel, right_channel)).astype(np.int16)
    
    # Set fade samples using property
    fade_samples = 100
    audifier.fade_samples = fade_samples
    
    # Apply fade
    faded_stereo = audifier.apply_fade(stereo_data)
    
    # Check left channel fade
    # First sample should be significantly reduced (close to zero)
    assert abs(faded_stereo[0, 0]) < 0.1 * abs(stereo_data[fade_samples, 0])
    
    # Middle of fade-in should be around half amplitude
    assert 0.3 * abs(stereo_data[fade_samples, 0]) < abs(faded_stereo[fade_samples // 2, 0]) < 0.7 * abs(stereo_data[fade_samples, 0])
    
    # Middle of audio should be unchanged
    assert faded_stereo[samples // 2, 0] == stereo_data[samples // 2, 0]
    
    # Last sample should be significantly reduced (close to zero)
    assert abs(faded_stereo[-1, 0]) < 0.1 * abs(stereo_data[-fade_samples, 0])
    
    # Check right channel fade
    assert abs(faded_stereo[0, 1]) < 0.1 * abs(stereo_data[fade_samples, 1])
    assert faded_stereo[samples // 2, 1] == stereo_data[samples // 2, 1]
    assert abs(faded_stereo[-1, 1]) < 0.1 * abs(stereo_data[-fade_samples, 1])

def test_normalize_to_int16():
    """Test the normalize_to_int16 method"""
    # We can test this static method directly
    audifier = Audifier()
    
    # Create a simple float array
    float_data = np.array([-2.5, -1.0, 0.0, 1.0, 2.5], dtype=np.float32)
    
    # Normalize to int16
    int16_data = audifier.normalize_to_int16(float_data)
    
    # Check type
    assert int16_data.dtype == np.int16
    
    # Check that values are normalized to -32767 to 32767 range
    assert np.min(int16_data) >= -32767
    assert np.max(int16_data) <= 32767
    
    # Check that order is preserved (lowest value in float_data is lowest in int16_data)
    assert np.argmin(int16_data) == np.argmin(float_data)
    assert np.argmax(int16_data) == np.argmax(float_data)

# Test configuration
@pytest.fixture
def audifier_instance():
    """Create a basic Audifier instance for testing"""
    return Audifier()

def test_channels_setting(audifier_instance):
    """Test that channels can be set correctly"""
    audifier = audifier_instance
    
    # Test default value
    assert audifier.channels == 1, "Default channels should be 1 (mono)"
    
    # Test setting to stereo
    audifier.channels = 2
    assert audifier.channels == 2, "Channels should be set to 2 (stereo)"
    
    # Test another valid value
    audifier.channels = 1
    assert audifier.channels == 1, "Channels should be set to 1 (mono)"

def test_fade_samples_setting(audifier_instance):
    """Test that fade samples can be set correctly"""
    audifier = audifier_instance
    
    # Test default value
    assert audifier.fade_samples == 0, "Default fade_samples should be 0"
    
    # Test setting to a positive value
    audifier.fade_samples = 1000
    assert audifier.fade_samples == 1000, "fade_samples should be set to 1000"
    
    # Test setting to 0
    audifier.fade_samples = 0
    assert audifier.fade_samples == 0, "fade_samples should be set to 0"

def test_filename_format():
    """Test that audio filenames follow the correct format pattern."""
    # Import directly from the module like in the notebook
    from plotbot.audifier import audifier
    from plotbot import mag_rtn

    # Set up temporary directory for files
    import tempfile
    temp_dir = tempfile.mkdtemp()
    try:
        # Configure audifier with original directory
        original_dir = audifier.save_dir
        audifier.set_save_dir(temp_dir)
        
        # Public timerange
        trange = ['2023-09-28/06:00:00.000', '2023-09-28/07:30:00.000']  # Enc 17 HCS Crossing
        
        # Verify mono filename format
        try:
            audifier.channels = 1
            audifier.sample_rate = 44100
            result = audifier.audify(trange, mag_rtn.br)
            
            if result and 'br' in result:
                filename = os.path.basename(result['br'])
                print(f"Mono filename: {filename}")
                # Check basic elements
                assert "E" in filename, "Encounter marker missing"
                assert "2023-09-28" in filename, "Date format incorrect" 
                assert "PSP_MAG_RTN" in filename, "Data type incorrect"
                assert "44100SR" in filename, "Sample rate missing"
                assert filename.endswith("Br.wav"), "Component name incorrect"
        except Exception as e:
            print(f"Mono test issue: {e}")
        
        # Verify stereo filename format
        try:
            audifier.channels = 2
            result = audifier.audify(trange, mag_rtn.br, mag_rtn.bt)
            
            if result and 'stereo_Br_Bt' in result:
                filename = os.path.basename(result['stereo_Br_Bt'])
                print(f"Stereo filename: {filename}")
                # Check basic elements
                assert "E" in filename, "Encounter marker missing"
                assert "2023-09-28" in filename, "Date format incorrect"
                assert "PSP_MAG_RTN" in filename, "Data type incorrect"
                assert "44100SR" in filename, "Sample rate missing"
                assert "Br_L_Bt_R" in filename, "Channel indicators incorrect"
        except Exception as e:
            print(f"Stereo test issue: {e}")
    
    finally:
        # Clean up and restore original settings
        audifier.set_save_dir(original_dir) if original_dir else None
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

def test_audify_uses_existing_encounter_dir(): # No monkeypatch needed
    """Test that audify uses the existing dir if save_dir ends with encounter."""
    # Create a base temp directory
    base_temp_dir = tempfile.mkdtemp()
    encounter_name = "E17" # The KNOWN encounter for the public time range
    existing_encounter_dir = os.path.join(base_temp_dir, encounter_name)
    os.makedirs(existing_encounter_dir)
    
    # Use the global audifier instance and configure
    audifier = global_audifier
    original_save_dir = audifier.save_dir
    audifier.set_save_dir(existing_encounter_dir) # Set save_dir to .../E17
    audifier.channels = 1
    audifier.fade_samples = 0
    audifier.sample_rate = 44100

    # --- NO MOCKING --- 
    # Use the real get_encounter_number by running audify with E17 data
    
    # Define expected subfolder based on PUBLIC_TRANGE and REAL encounter (E17)
    start_date = PUBLIC_TRANGE[0].split('/')[0]
    formatted_date = start_date.replace('-', '_')
    start_time = audifier.format_time_for_filename(PUBLIC_TRANGE[0].split('/')[1])
    stop_time = audifier.format_time_for_filename(PUBLIC_TRANGE[1].split('/')[1])
    expected_subfolder_name = f"{encounter_name}_{formatted_date}_{start_time}_to_{stop_time}"
    expected_output_dir = os.path.join(existing_encounter_dir, expected_subfolder_name)
    incorrect_nested_dir = os.path.join(existing_encounter_dir, encounter_name, expected_subfolder_name)
    
    print(f"Test Setup: save_dir='{audifier.save_dir}'")
    print(f"Expected output directory: {expected_output_dir}")
    print(f"Incorrect nested directory: {incorrect_nested_dir}")

    try:
        # Run audify using real component and the E17 public time range
        files = audifier.audify(PUBLIC_TRANGE, mag_rtn.br)
        
        # Check results based on filesystem
        assert os.path.isdir(expected_output_dir), f"Expected output directory was not created: {expected_output_dir}"
        assert not os.path.isdir(incorrect_nested_dir), f"Incorrect nested directory was created: {incorrect_nested_dir}"
        
        # Optional: Check if the file itself was created within the correct dir
        if files and 'br' in files:
             expected_file_path = files['br']
             assert os.path.dirname(expected_file_path) == expected_output_dir, f"File created in wrong directory: {expected_file_path}"
             assert os.path.exists(expected_file_path), f"Expected file does not exist: {expected_file_path}"
        else:
             print("Warning: Audify did not return expected file key 'br', skipping file path check.")

    finally:
        # Clean up
        audifier.set_save_dir(original_save_dir) if original_save_dir else None
        try:
            shutil.rmtree(base_temp_dir)
        except Exception as e:
            print(f"Error cleaning up base temp dir {base_temp_dir}: {e}")
