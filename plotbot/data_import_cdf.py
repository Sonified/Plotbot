"""
plotbot/data_import_cdf.py

CDF Metadata Scanner and Dynamic Class Generator

This module provides functionality to:
1. Scan CDF files and extract metadata (variables, attributes, structures)
2. Generate dynamic plotbot-compatible variable classes
3. Cache metadata for reuse
4. Create .pyi type hint files for discovered structures

Integrates with plotbot's existing data architecture while providing
clean separation of CDF-specific functionality.
"""

import cdflib
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import namedtuple
import re
import inspect

from .print_manager import print_manager
from .time_utils import daterange
from .config import config

# Metadata structures
CDFVariableInfo = namedtuple('CDFVariableInfo', [
    'name', 'data_type', 'shape', 'plot_type', 'units', 'description',
    'colormap', 'colorbar_scale', 'colorbar_limits', 'y_scale', 'y_label',
    'colorbar_label', 'depend_1'  # Store DEPEND_1 attribute for frequency data
])

CDFMetadata = namedtuple('CDFMetadata', [
    'file_path', 'variables', 'time_variable', 'frequency_variable', 
    'global_attributes', 'variable_count', 'scan_timestamp',
    'start_time', 'end_time', 'time_coverage_hours'  # Time range info for fast filtering!
])

class CDFMetadataScanner:
    """
    Scans CDF files and extracts metadata for plotbot integration.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the CDF metadata scanner.
        
        Args:
            cache_dir: Directory to store metadata cache (default: plotbot/cache/cdf_metadata)
        """
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), 'cache', 'cdf_metadata')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def scan_cdf_file(self, file_path: str, force_rescan: bool = False) -> Optional[CDFMetadata]:
        """
        Scan a single CDF file and extract metadata.
        
        Args:
            file_path: Path to the CDF file
            force_rescan: If True, ignore cached metadata and rescan
            
        Returns:
            CDFMetadata object or None if scan fails
        """
        print_manager.debug(f"🔍 Scanning CDF file: {os.path.basename(file_path)}")
        
        # Check cache first
        cache_file = self._get_cache_file_path(file_path)
        if not force_rescan and os.path.exists(cache_file):
            try:
                cached_metadata = self._load_cached_metadata(cache_file)
                if cached_metadata:
                    print_manager.debug(f"  📋 Using cached metadata for {os.path.basename(file_path)}")
                    return cached_metadata
            except Exception as e:
                print_manager.warning(f"  ⚠️ Failed to load cached metadata: {e}")
        
        # Perform fresh scan
        try:
            with cdflib.CDF(file_path) as cdf_file:
                metadata = self._extract_metadata(cdf_file, file_path)
                
            # Cache the results
            self._save_metadata_cache(cache_file, metadata)
            
            print_manager.debug(f"  ✅ Scanned {metadata.variable_count} variables from {os.path.basename(file_path)}")
            return metadata
            
        except Exception as e:
            print_manager.error(f"  ❌ Failed to scan CDF file {file_path}: {e}")
            return None
    
    def _extract_metadata(self, cdf_file, file_path: str) -> CDFMetadata:
        """Extract metadata from an open CDF file."""
        cdf_info = cdf_file.cdf_info()
        global_attrs = cdf_file.globalattsget()
        
        # Clean up duplicate global attributes
        cleaned_global_attrs = self._clean_global_attributes(global_attrs)
        
        # Find time and frequency variables
        all_vars = cdf_info.zVariables + cdf_info.rVariables
        time_var = self._find_time_variable(all_vars, cdf_file)
        freq_var = self._find_frequency_variable(all_vars, cdf_file)
        
        print_manager.debug(f"    Time variable: {time_var}")
        print_manager.debug(f"    Frequency variable: {freq_var}")
        
        # Extract variable metadata
        variables = []
        for var_name in all_vars:
            # Don't skip variables that are referenced as DEPEND_1 by other variables
            is_depend_var = False
            for check_var in all_vars:
                try:
                    check_attrs = cdf_file.varattsget(check_var)
                    if check_attrs.get('DEPEND_1') == var_name:
                        is_depend_var = True
                        break
                except:
                    continue
            
            # Skip time/frequency vars unless they're needed as DEPEND_1
            if var_name in [time_var, freq_var] and not is_depend_var:
                continue
                
            try:
                var_info = self._extract_variable_info(var_name, cdf_file, time_var, freq_var)
                if var_info:
                    variables.append(var_info)
                    print_manager.debug(f"      📊 {var_name}: {var_info.plot_type}")
                    
            except Exception as e:
                print_manager.warning(f"    ⚠️ Failed to process variable {var_name}: {e}")
        
        # Extract time boundaries for fast filtering
        start_time_str, end_time_str, coverage_hours = self._extract_time_boundaries(cdf_file, time_var)
        
        return CDFMetadata(
            file_path=file_path,
            variables=variables,
            time_variable=time_var,
            frequency_variable=freq_var,
            global_attributes=cleaned_global_attrs,
            variable_count=len(variables),
            scan_timestamp=datetime.now().isoformat(),
            start_time=start_time_str,
            end_time=end_time_str,
            time_coverage_hours=coverage_hours
        )
    
    def _clean_global_attributes(self, global_attrs: Dict) -> Dict:
        """
        Clean up global attributes by deduplicating identical values in lists.
        
        Args:
            global_attrs: Raw global attributes from CDF file
            
        Returns:
            Cleaned global attributes with duplicates removed
        """
        cleaned_attrs = {}
        
        for key, value in global_attrs.items():
            if isinstance(value, list) and len(value) > 1:
                # Check if all values in the list are identical
                unique_values = list(set(value))
                if len(unique_values) == 1:
                    # All values are identical - keep only one
                    cleaned_attrs[key] = unique_values[0]
                    print_manager.debug(f"    🧹 Deduplicated {key}: {len(value)} → 1 (all identical)")
                elif len(unique_values) < len(value):
                    # Some duplicates - keep unique values only
                    cleaned_attrs[key] = unique_values
                    print_manager.debug(f"    🧹 Deduplicated {key}: {len(value)} → {len(unique_values)}")
                else:
                    # All values are unique - keep as-is
                    cleaned_attrs[key] = value
            else:
                # Single value or empty list - keep as-is
                cleaned_attrs[key] = value
        
        return cleaned_attrs
    
    def _find_time_variable(self, all_vars: List[str], cdf_file) -> Optional[str]:
        """Find the primary time variable in the CDF file."""
        time_candidates = [
            var for var in all_vars 
            if any(keyword in var.lower() for keyword in ['epoch', 'time', 'fft_time'])
        ]
        
        if not time_candidates:
            return None
            
        # Prefer more specific time variables
        for preferred in ['FFT_time', 'Epoch', 'TIME']:
            if preferred in time_candidates:
                return preferred
                
        return time_candidates[0]
    
    def _find_frequency_variable(self, all_vars: List[str], cdf_file) -> Optional[str]:
        """Find the frequency variable in the CDF file."""
        freq_candidates = [
            var for var in all_vars 
            if any(keyword in var.lower() for keyword in ['freq', 'frequencies'])
        ]
        
        if not freq_candidates:
            return None
            
        # Prefer more specific frequency variables
        for preferred in ['Frequencies', 'frequency', 'freq']:
            if preferred in freq_candidates:
                return preferred
                
        return freq_candidates[0]
    
    def _extract_variable_info(self, var_name: str, cdf_file, time_var: str, freq_var: str) -> Optional[CDFVariableInfo]:
        """Extract metadata for a single variable."""
        try:
            # Get variable attributes
            var_attrs = cdf_file.varattsget(var_name)
            var_info = cdf_file.varinq(var_name)
            
            # Get a sample of the data to determine shape
            try:
                sample_data = cdf_file.varget(var_name, startrec=0, endrec=min(10, var_info.Last_Rec))
                if sample_data is not None:
                    data_shape = sample_data.shape
                else:
                    data_shape = (0,)
            except:
                data_shape = (0,)
            
            # Determine plot type using DISPLAY_TYPE and DEPEND attributes (like tplot)
            plot_type = self._determine_plot_type(var_name, data_shape, var_attrs, time_var, freq_var)
            
            # Extract units and description
            units = var_attrs.get('UNITS', var_attrs.get('units', ''))
            description = var_attrs.get('CATDESC', var_attrs.get('FIELDNAM', var_name))
            
            # Get visualization parameters
            colormap, colorbar_scale, colorbar_limits = self._get_visualization_params(var_name, var_attrs)
            y_scale, y_label = self._get_axis_params(var_name, var_attrs, units)
            
            # Generate colorbar label using LaTeX-formatted units
            colorbar_label = self._format_units_for_latex(units) if units.strip() else None
            
            return CDFVariableInfo(
                name=var_name,
                data_type=var_info.Data_Type_Description,
                shape=data_shape,
                plot_type=plot_type,
                units=units,
                description=description,
                colormap=colormap,
                colorbar_scale=colorbar_scale,
                colorbar_limits=colorbar_limits,
                y_scale=y_scale,
                y_label=y_label,
                colorbar_label=colorbar_label,
                depend_1=var_attrs.get('DEPEND_1', None)
            )
            
        except Exception as e:
            print_manager.warning(f"    ⚠️ Error extracting info for {var_name}: {e}")
            return None
    
    def _determine_plot_type(self, var_name: str, shape: Tuple, var_attrs: Dict, time_var: str, freq_var: str) -> str:
        """Determine the appropriate plot type using DISPLAY_TYPE and DEPEND attributes (like tplot)."""
        # First check DISPLAY_TYPE attribute (most reliable, like tplot)
        display_type = var_attrs.get('DISPLAY_TYPE', '').lower()
        if display_type == 'spectrogram':
            return 'spectral'
        
        # Check for DEPEND_1 attribute (indicates Y-axis dependency, likely frequency)
        depend_1 = var_attrs.get('DEPEND_1', None)
        if depend_1:
            print_manager.debug(f"      🔗 {var_name} DEPEND_1: {depend_1}")
            # If it has DEPEND_1 and is 2D, it's likely spectral
            if len(shape) >= 2:
                return 'spectral'
        
        # Fallback to shape analysis
        # Check for spectral data (2D with frequency dimension)
        if len(shape) >= 2 and any(keyword in var_name.lower() for keyword in 
                                  ['power', 'spectral', 'ellipticity', 'coherency', 'wave']):
            return 'spectral'
        
        # Check for time series data (1D)
        elif len(shape) == 1 or (len(shape) == 2 and shape[1] == 1):
            return 'timeseries'
        
        # Check for vector data (Nx3 for x,y,z components)
        elif len(shape) == 2 and shape[1] == 3:
            return 'vector'
        
        # Default to timeseries for 1D data
        else:
            return 'timeseries'
    
    def _get_visualization_params(self, var_name: str, var_attrs: Dict) -> Tuple[str, str, Optional[Tuple]]:
        """Determine colormap, scale, and limits for visualization."""
        # Default colormap
        colormap = 'turbo'  # Good for spectral data
        
        # Determine scale based on variable name and attributes
        if any(keyword in var_name.lower() for keyword in ['power', 'spectral']):
            colorbar_scale = 'log'
        else:
            colorbar_scale = 'linear'
        
        # Extract limits from attributes if available
        colorbar_limits = None
        if 'SCALEMIN' in var_attrs and 'SCALEMAX' in var_attrs:
            try:
                vmin = float(var_attrs['SCALEMIN'])
                vmax = float(var_attrs['SCALEMAX'])
                colorbar_limits = (vmin, vmax)
            except (ValueError, TypeError):
                pass
        
        return colormap, colorbar_scale, colorbar_limits
    
    def _format_units_for_latex(self, units: str) -> str:
        """Convert CDF unit notation to LaTeX for proper matplotlib rendering.
        
        Handles both common CDF notation styles:
        - !U2!N style (found in PSP wave files): nT!U2!N/Hz → nT²/Hz  
        - [U2] style (alternative format): nT[U2]/Hz → nT²/Hz
        """
        if not units:
            return ""
        
        # Strip whitespace and return empty if only whitespace
        units = units.strip()
        if not units:
            return ""
        
        # Convert common CDF unit patterns to LaTeX
        formatted = units
        
        # Handle CDF-style !U2!N notation (actual format found in PSP files)
        formatted = formatted.replace('!U2!N', r'$^2$')
        formatted = formatted.replace('!U3!N', r'$^3$')
        formatted = formatted.replace('!U-1!N', r'$^{-1}$')
        formatted = formatted.replace('!U-2!N', r'$^{-2}$')
        formatted = formatted.replace('!U-3!N', r'$^{-3}$')
        
        # Handle alternative [U2] bracket notation 
        formatted = formatted.replace('[U2]', r'$^2$')
        formatted = formatted.replace('[U3]', r'$^3$')
        formatted = formatted.replace('[U-1]', r'$^{-1}$')
        formatted = formatted.replace('[U-2]', r'$^{-2}$')
        formatted = formatted.replace('[U-3]', r'$^{-3}$')
        
        # Handle generic patterns with regex for any number
        # CDF !Uxx!N format (e.g., !U4!N, !U-5!N)
        formatted = re.sub(r'!U(\d+)!N', r'$^{\1}$', formatted)
        formatted = re.sub(r'!U-(\d+)!N', r'$^{-\1}$', formatted)
        
        # Alternative [Uxx] bracket format (e.g., [U4], [U-5])
        formatted = re.sub(r'\[U(\d+)\]', r'$^{\1}$', formatted)
        formatted = re.sub(r'\[U-(\d+)\]', r'$^{-\1}$', formatted)
        
        # Handle special cases like !a-2!n (found in S_mag variable)
        formatted = formatted.replace('!a-2!n', r'$^{-2}$')
        
        # Final cleanup - strip again in case formatting added whitespace
        formatted = formatted.strip()
        
        return formatted

    def _get_axis_params(self, var_name: str, var_attrs: dict, units: str) -> tuple:
        """Determine appropriate axis scaling and labeling."""
        # Format units for proper LaTeX rendering
        formatted_units = self._format_units_for_latex(units)
        
        # Determine Y scale
        if any(keyword in var_name.lower() for keyword in ['freq', 'frequencies']):
            y_scale = 'log'
            y_label = f'Frequency ({formatted_units})' if formatted_units else 'Frequency'
        else:
            y_scale = 'linear'
            y_label = f'{var_name} ({formatted_units})' if formatted_units else var_name
        
        return y_scale, y_label
    
    def _extract_time_boundaries(self, cdf_file, time_var: str) -> Tuple[str, str, float]:
        """
        Extract start and end times from CDF file for fast filtering.
        
        Args:
            cdf_file: Open CDF file object
            time_var: Name of the time variable
            
        Returns:
            Tuple of (start_time_str, end_time_str, coverage_hours)
        """
        try:
            if not time_var:
                return None, None, 0.0
            
            # Get time variable info
            var_info = cdf_file.varinq(time_var)
            n_records = var_info.Last_Rec + 1
            
            if n_records <= 0:
                return None, None, 0.0
            
            print_manager.debug(f"    ⏱️  Extracting time boundaries from {n_records} records")
            
            # Read first and last time points efficiently
            first_time_raw = cdf_file.varget(time_var, startrec=0, endrec=0)
            last_time_raw = cdf_file.varget(time_var, startrec=n_records-1, endrec=n_records-1)
            
            if first_time_raw is None or last_time_raw is None:
                return None, None, 0.0
            
            # Handle array vs scalar returns
            first_time = first_time_raw[0] if hasattr(first_time_raw, '__getitem__') and len(first_time_raw) > 0 else first_time_raw
            last_time = last_time_raw[0] if hasattr(last_time_raw, '__getitem__') and len(last_time_raw) > 0 else last_time_raw
            
            # Convert to plotbot's standard time format directly (most efficient path)
            try:
                # Use cdflib's encode_tt2000 for direct string conversion (no datetime objects needed)
                first_iso_str = cdflib.cdfepoch.encode_tt2000(first_time)
                last_iso_str = cdflib.cdfepoch.encode_tt2000(last_time)
                
                # Convert from ISO format to plotbot format with simple string manipulation
                # ISO: '2021-04-29T00:00:01.748711936' → Plotbot: '2021/04/29 00:00:01.748'
                start_time_str = first_iso_str.replace('-', '/').replace('T', ' ')[:23]  # Trim to milliseconds
                end_time_str = last_iso_str.replace('-', '/').replace('T', ' ')[:23]    # Trim to milliseconds
                
                # Calculate coverage in hours using the raw time values directly
                coverage_hours = (last_time - first_time) / 1e9 / 3600.0  # TT2000 is nanoseconds
                
                print_manager.debug(f"    📅 Time range: {start_time_str} to {end_time_str}")
                print_manager.debug(f"    ⏳ Coverage: {coverage_hours:.2f} hours")
                
                return start_time_str, end_time_str, coverage_hours
                
            except Exception as e:
                print_manager.warning(f"    ⚠️  Failed to convert time boundaries: {e}")
                return None, None, 0.0
            
        except Exception as e:
            print_manager.warning(f"    ⚠️  Failed to extract time boundaries: {e}")
            return None, None, 0.0
    
    def _get_cache_file_path(self, file_path: str) -> str:
        """Generate cache file path for a CDF file."""
        file_basename = os.path.basename(file_path)
        cache_name = f"{file_basename}.metadata.json"
        return os.path.join(self.cache_dir, cache_name)
    
    def _save_metadata_cache(self, cache_file: str, metadata: CDFMetadata):
        """Save metadata to cache file."""
        try:
            # Convert namedtuples to dicts for JSON serialization
            cache_data = {
                'file_path': metadata.file_path,
                'time_variable': metadata.time_variable,
                'frequency_variable': metadata.frequency_variable,
                'global_attributes': metadata.global_attributes,
                'variable_count': metadata.variable_count,
                'scan_timestamp': metadata.scan_timestamp,
                'start_time': metadata.start_time,
                'end_time': metadata.end_time,
                'time_coverage_hours': metadata.time_coverage_hours,
                'variables': [
                    {
                        'name': var.name,
                        'data_type': var.data_type,
                        'shape': var.shape,
                        'plot_type': var.plot_type,
                        'units': var.units,
                        'description': var.description,
                        'colormap': var.colormap,
                        'colorbar_scale': var.colorbar_scale,
                        'colorbar_limits': var.colorbar_limits,
                        'y_scale': var.y_scale,
                        'y_label': var.y_label
                    }
                    for var in metadata.variables
                ]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print_manager.warning(f"Failed to save metadata cache: {e}")
    
    def _load_cached_metadata(self, cache_file: str) -> Optional[CDFMetadata]:
        """Load metadata from cache file."""
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Convert back to namedtuples
            variables = [
                CDFVariableInfo(
                    name=var['name'],
                    data_type=var['data_type'],
                    shape=tuple(var['shape']),
                    plot_type=var['plot_type'],
                    units=var['units'],
                    description=var['description'],
                    colormap=var['colormap'],
                    colorbar_scale=var['colorbar_scale'],
                    colorbar_limits=tuple(var['colorbar_limits']) if var['colorbar_limits'] else None,
                    y_scale=var['y_scale'],
                    y_label=var['y_label']
                )
                for var in cache_data['variables']
            ]
            
            return CDFMetadata(
                file_path=cache_data['file_path'],
                variables=variables,
                time_variable=cache_data['time_variable'],
                frequency_variable=cache_data['frequency_variable'],
                global_attributes=cache_data['global_attributes'],
                variable_count=cache_data['variable_count'],
                scan_timestamp=cache_data['scan_timestamp'],
                start_time=cache_data.get('start_time'),
                end_time=cache_data.get('end_time'),
                time_coverage_hours=cache_data.get('time_coverage_hours', 0.0)
            )
            
        except Exception as e:
            print_manager.warning(f"Failed to load cached metadata: {e}")
            return None


def filter_cdf_files_by_time(file_paths: List[str], start_time: datetime, end_time: datetime) -> List[str]:
    """
    Filter CDF files by time range using cached metadata for lightning-fast filtering.
    
    Args:
        file_paths: List of CDF file paths to check
        start_time: Start of requested time range
        end_time: End of requested time range
        
    Returns:
        List of file paths that contain data in the requested time range
    """
    scanner = CDFMetadataScanner()
    relevant_files = []
    
    print_manager.debug(f"🔍 Filtering {len(file_paths)} CDF files by time range")
    
    for file_path in file_paths:
        try:
            # Try to get cached metadata first (super fast!)
            metadata = scanner.scan_cdf_file(file_path, force_rescan=False)
            
            if not metadata or not metadata.start_time or not metadata.end_time:
                # No time info available, include it to be safe
                relevant_files.append(file_path)
                print_manager.debug(f"    📄 {os.path.basename(file_path)}: No time info, including")
                continue
            
            # Parse cached time boundaries
            try:
                from dateutil.parser import parse
                file_start = parse(metadata.start_time)
                file_end = parse(metadata.end_time)
                
                # Check for overlap: file_start <= requested_end AND file_end >= requested_start
                has_overlap = file_start <= end_time and file_end >= start_time
                
                if has_overlap:
                    relevant_files.append(file_path)
                    print_manager.debug(f"    ✅ {os.path.basename(file_path)}: {metadata.time_coverage_hours:.1f}h overlap")
                else:
                    print_manager.debug(f"    ❌ {os.path.basename(file_path)}: No overlap")
                    
            except Exception as e:
                # If time parsing fails, include it to be safe
                relevant_files.append(file_path)
                print_manager.debug(f"    ⚠️  {os.path.basename(file_path)}: Time parsing failed, including")
                
        except Exception as e:
            # If metadata reading fails, include it to be safe
            relevant_files.append(file_path)
            print_manager.debug(f"    ❌ {os.path.basename(file_path)}: Metadata error, including")
    
    print_manager.debug(f"🎯 Filtered to {len(relevant_files)}/{len(file_paths)} files with time overlap")
    return relevant_files


def scan_cdf_directory(directory_path: str, file_pattern: str = "*.cdf") -> Dict[str, CDFMetadata]:
    """
    Scan all CDF files in a directory and return metadata.
    
    Args:
        directory_path: Directory containing CDF files
        file_pattern: File pattern to match (default: "*.cdf")
        
    Returns:
        Dictionary mapping file paths to CDFMetadata objects
    """
    scanner = CDFMetadataScanner()
    metadata_dict = {}
    
    print_manager.debug(f"🔍 Scanning CDF directory: {directory_path}")
    
    if not os.path.exists(directory_path):
        print_manager.error(f"Directory does not exist: {directory_path}")
        return metadata_dict
    
    # Find all CDF files
    import glob
    pattern_path = os.path.join(directory_path, file_pattern)
    cdf_files = glob.glob(pattern_path)
    
    print_manager.debug(f"  Found {len(cdf_files)} CDF files")
    
    for file_path in cdf_files:
        metadata = scanner.scan_cdf_file(file_path)
        if metadata:
            metadata_dict[file_path] = metadata
    
    print_manager.status(f"📋 Scanned {len(metadata_dict)} CDF files successfully")
    return metadata_dict


def create_dynamic_cdf_class(metadata: CDFMetadata, class_name: str) -> str:
    """
    Generate Python class code for a CDF file's variables.
    
    Args:
        metadata: CDFMetadata object from scanning
        class_name: Name for the generated class
        
    Returns:
        Python class code as string
    """
    class_code = f'''"""
Auto-generated CDF variable class for {os.path.basename(metadata.file_path)}
Generated on: {datetime.now().isoformat()}
"""

class {class_name}:
    """
    CDF Variables from {os.path.basename(metadata.file_path)}
    
    Contains {metadata.variable_count} variables:
{chr(10).join(f"    - {var.name}: {var.description}" for var in metadata.variables)}
    """
    
    def __init__(self):
        self.file_path = "{metadata.file_path}"
        self.time_variable = "{metadata.time_variable}"
        self.frequency_variable = "{metadata.frequency_variable}"
        self.variable_count = {metadata.variable_count}
        
'''
    
    # Add variable definitions
    for var in metadata.variables:
        var_code = f'''    
    # {var.description}
    class {var.name}:
        name = "{var.name}"
        data_type = "{var.data_type}"
        plot_type = "{var.plot_type}"
        units = "{var.units}"
        colormap = "{var.colormap}"
        colorbar_scale = "{var.colorbar_scale}"
        colorbar_limits = {var.colorbar_limits}
        y_scale = "{var.y_scale}"
        y_label = "{var.y_label}"
        shape = {var.shape}
        
'''
        class_code += var_code
    
    return class_code 


def cdf_to_plotbot(file_path: str, class_name: str, output_dir: Optional[str] = None) -> bool:
    """
    Generate a complete plotbot class from a CDF file.
    
    This function:
    1. Scans the CDF file using CDFMetadataScanner
    2. Generates a full plotbot class following existing patterns
    3. Creates both .py and .pyi files
    4. Makes the class immediately available for import
    
    Args:
        file_path: Path to the CDF file
        class_name: Name for the generated plotbot class (e.g., 'psp_waves')
        output_dir: Directory to write files (default: plotbot/data_classes/)
        
    Returns:
        True if successful, False otherwise
    """
    print_manager.status(f"🔧 Generating plotbot class '{class_name}' from {os.path.basename(file_path)}")
    
    # Set default output directory to custom_classes folder
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), 'data_classes', 'custom_classes')
    
    # Scan the CDF file
    scanner = CDFMetadataScanner()
    metadata = scanner.scan_cdf_file(file_path)
    
    if not metadata:
        print_manager.error(f"❌ Failed to scan CDF file: {file_path}")
        return False
    
    if not metadata.variables:
        print_manager.error(f"❌ No variables found in CDF file: {file_path}")
        return False
    
    print_manager.debug(f"  📊 Found {len(metadata.variables)} variables to process")
    
    # Generate the plotbot class code
    class_code = _generate_plotbot_class_code(metadata, class_name)
    pyi_code = _generate_plotbot_pyi_code(metadata, class_name)
    
    # Write the files
    py_file = os.path.join(output_dir, f"{class_name}.py")
    pyi_file = os.path.join(output_dir, f"{class_name}.pyi")
    
    try:
        # Write Python class file
        with open(py_file, 'w') as f:
            f.write(class_code)
        print_manager.debug(f"  📝 Written class file: {py_file}")
        
        # Write type hints file
        with open(pyi_file, 'w') as f:
            f.write(pyi_code)
        print_manager.debug(f"  📝 Written type hints: {pyi_file}")
        
        print_manager.status(f"✅ Successfully generated plotbot class '{class_name}'")
        print_manager.status(f"   📄 Class: {py_file}")
        print_manager.status(f"   📄 Types: {pyi_file}")
        print_manager.status(f"   🎯 Usage: from plotbot.data_classes.{class_name} import {class_name}")
        
        # IMMEDIATELY register the new class with data_cubby AND INJECT into globals
        print_manager.debug(f"🔄 Auto-registering '{class_name}' with data_cubby and injecting into globals...")
        try:
            import importlib
            import sys
            
            # Import the newly created module
            module_path = f"plotbot.data_classes.custom_classes.{class_name}"
            
            # Force reload if module already exists (for re-generation cases)
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
            
            module = importlib.import_module(module_path)
            
            # The class is initialized at the bottom of the generated file
            class_instance = getattr(module, class_name, None)
            
            if class_instance:
                # Add to the class type map for future lookups
                from .data_cubby import data_cubby
                data_cubby._CLASS_TYPE_MAP[class_name] = type(class_instance)
                
                # Inject the class instance into the caller's global namespace
                # This makes it immediately available, e.g., psp_waves_spectral.variable
                try:
                    caller_globals = inspect.stack()[1].frame.f_globals
                    caller_globals[class_name] = class_instance
                    print_manager.status(f"✅ Injected '{class_name}' into global namespace.")
                    print_manager.status(f"   🎯 Ready for direct use: {class_name}.<variable>")
                except Exception as e:
                    print_manager.warning(f"⚠️  Could not inject '{class_name}' into globals: {e}")

                print_manager.status(f"✅ Successfully registered '{class_name}' with data_cubby")
                print_manager.status(f"   📝 Class will auto-register on next plotbot restart")
            else:
                print_manager.warning(f"⚠️  Could not find class instance '{class_name}' in generated module")
                
        except Exception as e:
            print_manager.warning(f"⚠️  Failed to auto-register '{class_name}': {e}")
            print_manager.debug(f"   Manual registration may be needed on next plotbot restart")
        
        # AUTO-UPDATE MAIN __INIT__.PY for proper type hinting
        print_manager.status(f"🔄 Auto-updating main __init__.py for IDE type hinting...")
        try:
            if update_plotbot_init():
                print_manager.status(f"✅ Updated main __init__.py - IDE type hints now available!")
            else:
                print_manager.warning(f"⚠️  Failed to update __init__.py - type hints may not work in IDE")
        except Exception as e:
            print_manager.warning(f"⚠️  Error updating __init__.py: {e}")
        
        return True
        
    except Exception as e:
        print_manager.error(f"❌ Failed to write class files: {e}")
        return False


def _generate_plotbot_class_code(metadata: CDFMetadata, class_name: str) -> str:
    """Generate complete plotbot class code following existing patterns."""
    
    # Get base filename for comments
    base_filename = os.path.basename(metadata.file_path)
    
    # Generate raw_data keys from variables
    raw_data_keys = [f"'{var.name}': None" for var in metadata.variables]
    raw_data_dict = "{\n        " + ",\n        ".join(raw_data_keys) + "\n    }"
    
    # Generate variable processing in calculate_variables
    calc_vars_code = []
    set_ploptions_code = []
    
    # Identify spectral variables for mesh creation
    spectral_vars = [var.name for var in metadata.variables if var.plot_type == 'spectral']
    
    # Helper function for spectral plot options with debugging
    def generate_spectral_ploptions_with_debug(var):
        return f"""        # DEBUG: Setting up {var.name} (spectral)
        print_manager.dependency_management("=== PLOPTIONS DEBUG: {var.name} ===")
        {var.name}_data = self.raw_data.get('{var.name}')
        {var.name}_mesh = self.variable_meshes.get('{var.name}', self.datetime_array)
        {var.name}_additional = self.raw_data.get('{var.depend_1}', None)
        
        print_manager.dependency_management(f"  - Data shape: {{{var.name}_data.shape if {var.name}_data is not None else 'None'}}")
        print_manager.dependency_management(f"  - Mesh shape: {{{var.name}_mesh.shape if hasattr({var.name}_mesh, 'shape') else 'No shape attr'}}")
        print_manager.dependency_management(f"  - Additional data shape: {{{var.name}_additional.shape if {var.name}_additional is not None else 'None'}}")
        print_manager.dependency_management(f"  - Additional data type: {{type({var.name}_additional)}}")
        
        # CREATE 2D FREQUENCY MESH for additional_data (like EPAD does with pitch angles)
        if {var.name}_additional is not None and {var.name}_additional.ndim == 1:
            # Tile 1D frequency array to match time dimension (EXACTLY like DFB classes do)
            {var.name}_additional_2d = np.tile({var.name}_additional, (len(self.datetime_array), 1))
            print_manager.dependency_management(f"  - CONVERTED: 1D frequency {{{var.name}_additional.shape}} to 2D {{{var.name}_additional_2d.shape}}")
            {var.name}_additional = {var.name}_additional_2d
        
        self.{var.name} = plot_manager(
            {var.name}_data,
            plot_options=ploptions(
                data_type='{class_name}',
                var_name='{var.name}',
                class_name='{class_name}',
                subclass_name='{var.name}',
                plot_type='spectral',
                datetime_array={var.name}_mesh,
                y_label='{var.y_label}',
                legend_label='{var.description}',
                color=None,
                y_scale='{var.y_scale}',
                y_limit=None,
                line_width=1,
                line_style='-',
                additional_data={var.name}_additional,
                colormap='{var.colormap}',
                colorbar_scale='{var.colorbar_scale}',
                colorbar_limits={var.colorbar_limits},
                colorbar_label={repr(var.colorbar_label)}
            )
        )
        print_manager.dependency_management("=== END PLOPTIONS DEBUG ===")
"""
    
    for var in metadata.variables:
        # Variable calculation code
        if var.plot_type == 'spectral':
            calc_vars_code.append(f"""
        # Process {var.name} ({var.description})
        {var.name}_data = imported_data.data['{var.name}']
        
        # Handle fill values for {var.name}
        fill_val = imported_data.data.get('{var.name}_FILLVAL', -1e+38)
        {var.name}_data = np.where({var.name}_data == fill_val, np.nan, {var.name}_data)
        
        self.raw_data['{var.name}'] = {var.name}_data""")
        else:
            calc_vars_code.append(f"""
        # Process {var.name} ({var.description})
        {var.name}_data = imported_data.data['{var.name}']
        
        # Handle fill values for {var.name}
        fill_val = imported_data.data.get('{var.name}_FILLVAL', -1e+38)
        {var.name}_data = np.where({var.name}_data == fill_val, np.nan, {var.name}_data)
        
        self.raw_data['{var.name}'] = {var.name}_data""")
        
        # Plot options code
        if var.plot_type == 'spectral':
            set_ploptions_code.append(generate_spectral_ploptions_with_debug(var))
        else:
            set_ploptions_code.append(f"""        self.{var.name} = plot_manager(
            self.raw_data['{var.name}'],
            plot_options=ploptions(
                data_type='{class_name}',
                var_name='{var.name}',
                class_name='{class_name}',
                subclass_name='{var.name}',
                plot_type='time_series',
                datetime_array=self.datetime_array,
                y_label='{var.y_label}',
                legend_label='{var.description}',
                color='blue',
                y_scale='{var.y_scale}',
                y_limit=None,
                line_width=1,
                line_style='-'
            )
        )""")
    
    # Check if we need spectral data handling (times_mesh)
    has_spectral = any(var.plot_type == 'spectral' for var in metadata.variables)
    
    # Generate the complete class
    class_code = f'''"""
Auto-generated plotbot class for {base_filename}
Generated on: {datetime.now().isoformat()}
Source: {metadata.file_path}

This class contains {len(metadata.variables)} variables from the CDF file.
"""

import numpy as np
import pandas as pd
import cdflib
from datetime import datetime, timedelta, timezone
import logging

from plotbot.print_manager import print_manager
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions, retrieve_ploption_snapshot
from .._utils import _format_setattr_debug

class {class_name}_class:
    """
    CDF data class for {base_filename}
    
    Variables:
{chr(10).join(f"    - {var.name}: {var.description}" for var in metadata.variables)}
    """
    
    def __init__(self, imported_data):
        # Initialize basic attributes without triggering __setattr__ checks
        object.__setattr__(self, 'class_name', '{class_name}')
        object.__setattr__(self, 'data_type', '{class_name}')
        object.__setattr__(self, 'subclass_name', None)
        object.__setattr__(self, 'raw_data', {raw_data_dict})
        object.__setattr__(self, 'datetime', [])
        object.__setattr__(self, 'datetime_array', None)
        object.__setattr__(self, '_current_operation_trange', None)
        {"object.__setattr__(self, 'variable_meshes', {})" if has_spectral else ""}
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', '{metadata.file_path}')
        object.__setattr__(self, '_cdf_file_pattern', '{generate_file_pattern_from_cdf(metadata.file_path, os.path.dirname(metadata.file_path))}')

        if imported_data is None:
            self.set_ploptions()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management(f"Calculating {class_name} variables...")
            self.calculate_variables(imported_data)
            self.set_ploptions()
            print_manager.status(f"Successfully calculated {class_name} variables.")
        
        # Auto-register with data_cubby (following plotbot pattern)
        from plotbot.data_cubby import data_cubby
        data_cubby.stash(self, class_name='{class_name}')
        print_manager.dependency_management(f"Registered {class_name} with data_cubby")
    
    def update(self, imported_data, original_requested_trange=None):
        """Method to update class with new data."""
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{{self.__class__.__name__}}] Updated _current_operation_trange to: {{self._current_operation_trange}}")
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {{self.__class__.__name__}} update.")
            return
        
        print_manager.datacubby("\\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {{self.__class__.__name__}} update...")
        
        # Store current state before update
        current_state = {{}}
        for subclass_name in self.raw_data.keys():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                if hasattr(var, '_plot_state'):
                    current_state[subclass_name] = dict(var._plot_state)
                    print_manager.datacubby(f"Stored {{subclass_name}} state: {{retrieve_ploption_snapshot(current_state[subclass_name])}}")

        # Perform update
        self.calculate_variables(imported_data)
        self.set_ploptions()
        
        # Restore state
        print_manager.datacubby("Restoring saved state...")
        for subclass_name, state in current_state.items():
            if hasattr(self, subclass_name):
                var = getattr(self, subclass_name)
                var._plot_state.update(state)
                for attr, value in state.items():
                    if hasattr(var.plot_options, attr):
                        setattr(var.plot_options, attr, value)
                print_manager.datacubby(f"Restored {{subclass_name}} state: {{retrieve_ploption_snapshot(state)}}")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):
        """Retrieve a specific component"""
        print_manager.dependency_management(f"Getting subclass: {{subclass_name}}")
        if subclass_name in self.raw_data.keys():
            print_manager.dependency_management(f"Returning {{subclass_name}} component")
            return getattr(self, subclass_name)
        else:
            print(f"'{{subclass_name}}' is not a recognized subclass, friend!")
            print(f"Try one of these: {{', '.join(self.raw_data.keys())}}")
            return None

    def __getattr__(self, name):
        # Allow direct access to dunder OR single underscore methods/attributes
        if name.startswith('_'):
            try:
                return object.__getattribute__(self, name)
            except AttributeError:
                raise AttributeError(f"'{{self.__class__.__name__}}' object has no attribute '{{name}}'")

        if 'raw_data' not in self.__dict__:
            raise AttributeError(f"{{self.__class__.__name__}} has no attribute '{{name}}' (raw_data not initialized)")
        
        print_manager.dependency_management(f'{class_name} getattr helper!')
        available_attrs = list(self.raw_data.keys()) if self.raw_data else []
        print(f"'{{name}}' is not a recognized attribute, friend!")                
        print(f"Try one of these: {{', '.join(available_attrs)}}")
    
    def __setattr__(self, name, value):
        # Allow direct setting of dunder OR single underscore methods/attributes
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        # Allow setting known attributes
        print_manager.dependency_management(_format_setattr_debug(name, value))
        allowed_attrs = ['datetime', 'datetime_array', 'raw_data', 'time', 'field', 'variable_meshes', 'data_type']
        if name in allowed_attrs or name in self.raw_data:
            super().__setattr__(name, value)
        else:
            print_manager.dependency_management(f'{class_name} setattr helper!')
            print(f"'{{name}}' is not a recognized attribute, friend!")
            available_attrs = list(self.raw_data.keys()) if self.raw_data else []
            print(f"Try one of these: {{', '.join(available_attrs)}}")
            print_manager.dependency_management(f"Attempted to set unknown attribute: {{name}}")
    
    def calculate_variables(self, imported_data):
        """Calculate and store CDF variables"""
        # Dynamically find time variable from any CDF data
        time_var = None
        for var_name in imported_data.data.keys():
            if any(keyword in var_name.lower() for keyword in ['epoch', 'time', 'fft_time']):
                time_var = var_name
                break
        
        # Store time data
        if time_var and time_var in imported_data.data:
            self.time = np.asarray(imported_data.data[time_var])
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time))
            print_manager.dependency_management(f"Using time variable: {{time_var}}")
        else:
            # Fallback to imported_data.times if available
            self.time = np.asarray(imported_data.times) if hasattr(imported_data, 'times') else np.array([])
            self.datetime_array = np.array(cdflib.cdfepoch.to_datetime(self.time)) if len(self.time) > 0 else np.array([])
            print_manager.dependency_management("Using fallback times from imported_data.times")
        
        print_manager.dependency_management(f"self.datetime_array type: {{type(self.datetime_array)}}")
        print_manager.dependency_management(f"Datetime range: {{self.datetime_array[0] if len(self.datetime_array) > 0 else 'Empty'}} to {{self.datetime_array[-1] if len(self.datetime_array) > 0 else 'Empty'}}")
        
{chr(10).join(calc_vars_code)}
        
        {"# CREATE INDIVIDUAL MESHES FOR EACH 2D VARIABLE (mirror EPAD exactly)" if has_spectral else ""}
        {"# Store meshes in a dictionary for easy access" if has_spectral else ""}
        {"object.__setattr__(self, 'variable_meshes', {})" if has_spectral else ""}
        {"" if has_spectral else ""}
        {"print_manager.dependency_management(\"=== MESH CREATION DEBUG START ===\")" if has_spectral else ""}
        {"print_manager.dependency_management(f\"datetime_array shape: {self.datetime_array.shape if self.datetime_array is not None else 'None'}\")" if has_spectral else ""}
        {"print_manager.dependency_management(f\"datetime_array length: {len(self.datetime_array) if self.datetime_array is not None else 'None'}\")" if has_spectral else ""}
        {"" if has_spectral else ""}
        {"# For each 2D variable, create its own mesh (just like EPAD does for strahl)" if has_spectral else ""}
        {f"spectral_variables = {spectral_vars}" if has_spectral else ""}
        {"print_manager.dependency_management(f\"Spectral variables to process: {spectral_variables}\")" if has_spectral else ""}
        {"" if has_spectral else ""}
        {"for var_name in spectral_variables:" if has_spectral else ""}
        {"    var_data = self.raw_data.get(var_name)" if has_spectral else ""}
        {"    if var_data is not None:" if has_spectral else ""}
        {"        print_manager.dependency_management(f\"Processing {var_name}:\")" if has_spectral else ""}
        {"        print_manager.dependency_management(f\"  - Shape: {var_data.shape}\")" if has_spectral else ""}
        {"        print_manager.dependency_management(f\"  - ndim: {var_data.ndim}\")" if has_spectral else ""}
        {"        " if has_spectral else ""}
        {"        if var_data.ndim >= 2:" if has_spectral else ""}
        {"            print_manager.dependency_management(f\"  - Creating mesh with time_len={len(self.datetime_array)}, freq_len={var_data.shape[1]}\")" if has_spectral else ""}
        {"            " if has_spectral else ""}
        {"            # Create mesh for this specific variable (EXACTLY like EPAD)" if has_spectral else ""}
        {"            try:" if has_spectral else ""}
        {"                mesh_result = np.meshgrid(" if has_spectral else ""}
        {"                    self.datetime_array," if has_spectral else ""}
        {"                    np.arange(var_data.shape[1]),  # Use actual data dimensions" if has_spectral else ""}
        {"                    indexing='ij'" if has_spectral else ""}
        {"                )[0]" if has_spectral else ""}
        {"                self.variable_meshes[var_name] = mesh_result" if has_spectral else ""}
        {"                print_manager.dependency_management(f\"  - SUCCESS: Created mesh shape {mesh_result.shape}\")" if has_spectral else ""}
        {"            except Exception as mesh_error:" if has_spectral else ""}
        {"                print_manager.dependency_management(f\"  - ERROR creating mesh: {mesh_error}\")" if has_spectral else ""}
        {"                self.variable_meshes[var_name] = self.datetime_array" if has_spectral else ""}
        {"                print_manager.dependency_management(f\"  - FALLBACK: Using datetime_array\")" if has_spectral else ""}
        {"        else:" if has_spectral else ""}
        {"            print_manager.dependency_management(f\"  - SKIP: {var_name} is {var_data.ndim}D, not 2D+\")" if has_spectral else ""}
        {"    else:" if has_spectral else ""}
        {"        print_manager.dependency_management(f\"{var_name}: No data (None)\")" if has_spectral else ""}
        {"" if has_spectral else ""}
        {"print_manager.dependency_management(\"=== MESH CREATION DEBUG END ===\")" if has_spectral else ""}

        # Keep frequency arrays as 1D - individual meshes handle the 2D time dimension
        # Each spectral variable gets its own mesh in variable_meshes dictionary

        print_manager.dependency_management(f"Processed {{len([v for v in self.raw_data.values() if v is not None])}} variables successfully")
    
    def _find_frequency_data(self):
        """Dynamically find frequency data that matches spectral variables."""
        # Look for frequency variables that actually have data
        for var_name, var_data in self.raw_data.items():
            if ('freq' in var_name.lower() and 
                var_data is not None and 
                hasattr(var_data, '__len__') and 
                len(var_data) > 1):
                
                # Create frequency array that matches time dimension for pcolormesh
                # plotbot expects additional_data to be indexable by time
                if hasattr(self, 'datetime_array') and self.datetime_array is not None:
                    n_times = len(self.datetime_array)
                    n_freqs = len(var_data)
                    # Create 2D frequency array: each row is the same frequency values
                    freq_2d = np.tile(var_data, (n_times, 1))
                    return freq_2d
                else:
                    return var_data
        
        # Fallback - create a simple frequency array if nothing found
        # Assume 100 frequency bins from 10 Hz to 1 kHz
        freq_array = np.logspace(1, 3, 100)
        if hasattr(self, 'datetime_array') and self.datetime_array is not None:
            n_times = len(self.datetime_array)
            freq_2d = np.tile(freq_array, (n_times, 1))
            return freq_2d
        return freq_array
    
    def set_ploptions(self):
        """Set up plotting options for all variables"""
        print_manager.dependency_management("Setting up plot options for {class_name} variables")
        
{chr(10).join(set_ploptions_code)}

    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            setattr(self, key, value)

# Initialize the class with no data
{class_name} = {class_name}_class(None)
print_manager.dependency_management(f'initialized {class_name} class')
'''

    return class_code


def _generate_plotbot_pyi_code(metadata: CDFMetadata, class_name: str) -> str:
    """Generate type hints file for the plotbot class."""
    
    base_filename = os.path.basename(metadata.file_path)
    
    # Generate variable type hints
    variable_hints = []
    for var in metadata.variables:
        variable_hints.append(f"    {var.name}: plot_manager")
    
    pyi_code = f'''"""
Type hints for auto-generated plotbot class {class_name}
Generated on: {datetime.now().isoformat()}
Source: {base_filename}
"""

from typing import Optional, List, Dict, Any
from numpy import ndarray
from datetime import datetime
from plotbot.plot_manager import plot_manager
from plotbot.ploptions import ploptions

class {class_name}_class:
    """CDF data class for {base_filename}"""
    
    # Class attributes
    class_name: str
    data_type: str
    subclass_name: Optional[str]
    raw_data: Dict[str, Optional[ndarray]]
    datetime: List[datetime]
    datetime_array: Optional[ndarray]
    time: Optional[ndarray]
    times_mesh: Optional[ndarray]
    _current_operation_trange: Optional[List[str]]
    
    # Variable attributes
{chr(10).join(variable_hints)}
    
    def __init__(self, imported_data: Optional[Any]) -> None: ...
    def update(self, imported_data: Optional[Any], original_requested_trange: Optional[List[str]] = None) -> None: ...
    def get_subclass(self, subclass_name: str) -> Optional[plot_manager]: ...
    def calculate_variables(self, imported_data: Any) -> None: ...
    def set_ploptions(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

# Instance
{class_name}: {class_name}_class
'''

    return pyi_code 


def generate_file_pattern_from_cdf(cdf_file_path: str, search_directory: str = None) -> str:
    """
    Smart pattern generator that analyzes a CDF filename and creates a wildcard pattern
    that can find related files with different dates/versions/times.
    
    Args:
        cdf_file_path: Path to the original CDF file
        search_directory: Directory to search for similar files (for validation)
        
    Returns:
        File pattern with wildcards (e.g., "PSP_WaveAnalysis_*_v*.cdf")
        
    Examples:
        PSP_WaveAnalysis_2021-04-29_0600_v1.2.cdf → PSP_WaveAnalysis_*_v*.cdf
        psp_fld_l2_dfb_dc_spec_dv12hg_20211125_v01.cdf → psp_fld_l2_dfb_dc_spec_dv12hg_*_v*.cdf
        wi_h5_swe_00000000_v01.cdf → wi_h5_swe_*_v*.cdf
        custom_data_file.cdf → custom_data_file.cdf (no pattern found)
    """
    import re
    from pathlib import Path
    
    filename = os.path.basename(cdf_file_path)
    name_without_ext = filename.replace('.cdf', '')
    
    print_manager.debug(f"🔍 Analyzing filename: {filename}")
    
    # Define common date/time/version patterns to replace with wildcards
    # Order matters: process dates first, then times, then versions
    patterns_to_replace = [
        # Date patterns (must come first to avoid conflicts)
        (r'_\d{4}-\d{2}-\d{2}', '_*'),             # _YYYY-MM-DD (dash format)
        (r'_\d{8}(?=_|$)', '_*'),                  # _YYYYMMDD (compact format at word boundary)
        (r'\b\d{4}_\d{3}\b', '*'),                 # YYYY_DDD (day of year format)
        (r'00000000', '*'),                        # Placeholder dates (anywhere in name)
        
        # Time patterns (after date patterns to avoid conflicts)
        (r'_\d{4}(?=_v)', '_*'),                   # _HHMM before version
        (r'_\d{6}(?=_v)', '_*'),                   # _HHMMSS before version
        (r'_\d{4}(?=_)', '_*'),                    # _HHMM_ in middle
        (r'_\d{6}(?=_)', '_*'),                    # _HHMMSS_ in middle
        
        # Version patterns (must be precise to avoid false matches)
        (r'_v\d+\.\d+(?=\.cdf|$)', '_v*'),         # _v1.2, _v2.0 at end
        (r'_v\d{2,}(?=\.cdf|$)', '_v*'),           # _v01, _v02 at end (2+ digits to avoid v1v2)
        (r'_version\d+(?=\.cdf|$)', '_version*'),  # _version1, _version2 at end
        
        # Sequential numbering at end of filename
        (r'_\d{3}(?=\.cdf)', '_*'),               # _001, _002 at end
        (r'_\d{2}(?=\.cdf)', '_*'),               # _01, _02 at end
    ]
    
    # Apply pattern replacements
    pattern = name_without_ext
    replacements_made = []
    
    for regex_pattern, replacement in patterns_to_replace:
        matches = re.findall(regex_pattern, pattern)
        if matches:
            pattern = re.sub(regex_pattern, replacement, pattern)
            replacements_made.extend(matches)
    
    # Add .cdf extension back
    pattern += '.cdf'
    
    # Validate pattern by checking if it finds other files (if search directory provided)
    if search_directory and replacements_made:
        validation_files = _find_files_matching_pattern(pattern, search_directory)
        # Remove the original file from validation count
        validation_files = [f for f in validation_files if not f.endswith(filename)]
        
        if len(validation_files) == 0:
            print_manager.debug(f"  ⚠️  Pattern '{pattern}' found no other files, using exact filename")
            pattern = filename  # Fall back to exact match
        else:
            print_manager.debug(f"  ✅ Pattern '{pattern}' found {len(validation_files)} additional files")
    
    if replacements_made:
        print_manager.debug(f"  🎯 Generated pattern: {pattern}")
        print_manager.debug(f"  📝 Replaced: {', '.join(replacements_made)}")
    else:
        print_manager.debug(f"  📌 No patterns detected, using exact filename: {pattern}")
    
    return pattern


def _find_files_matching_pattern(pattern: str, directory: str) -> List[str]:
    """
    Find files matching a wildcard pattern in a directory.
    
    Args:
        pattern: Filename pattern with wildcards (e.g., "PSP_WaveAnalysis_*_v*.cdf")
        directory: Directory to search
        
    Returns:
        List of matching file paths
    """
    import glob
    
    if not os.path.exists(directory):
        return []
    
    # Convert simple wildcards to glob pattern
    glob_pattern = os.path.join(directory, pattern)
    matching_files = glob.glob(glob_pattern)
    
    return matching_files


# ============================================================================== 
# Auto-Init Updater for Plotbot Custom Classes
# 
# This script automatically scans the custom_classes directory and updates
# the main __init__.py file with the necessary imports and __all__ entries
# to ensure type hinting works properly.
# ==============================================================================

#!/usr/bin/env python3
"""
Auto-Init Updater for Plotbot Custom Classes

This script automatically scans the custom_classes directory and updates
the main __init__.py file with the necessary imports and __all__ entries
to ensure type hinting works properly.

Run this after generating new CDF classes.
"""

from pathlib import Path

def update_plotbot_init():
    """Update the main plotbot __init__.py with custom class imports."""
    
    # Find the plotbot root directory
    script_dir = Path(__file__).parent
    plotbot_root = script_dir.parent if script_dir.name == 'scripts' else script_dir
    init_file = plotbot_root / '__init__.py'
    custom_classes_dir = plotbot_root / 'data_classes' / 'custom_classes'
    
    if not custom_classes_dir.exists():
        print_manager.warning(f"❌ Custom classes directory not found: {custom_classes_dir}")
        return False
    
    if not init_file.exists():
        print_manager.error(f"❌ Init file not found: {init_file}")
        return False
    
    # Scan for custom classes
    custom_classes = []
    for py_file in custom_classes_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        class_name = py_file.stem
        custom_classes.append(class_name)
    
    if not custom_classes:
        print_manager.status("✅ No custom classes found - nothing to update")
        return True
    
    print_manager.debug(f"🔍 Found custom classes: {', '.join(custom_classes)}")
    
    # Read current init file
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Scan for existing imports to see what's already there vs what's missing
    existing_custom_imports = []
    for class_name in custom_classes:
        if f"from .data_classes.custom_classes.{class_name} import" in content:
            existing_custom_imports.append(class_name)
    
    missing_imports = [cls for cls in custom_classes if cls not in existing_custom_imports]
    
    if existing_custom_imports:
        print_manager.debug(f"✅ Already imported: {', '.join(existing_custom_imports)}")
    if missing_imports:
        print_manager.debug(f"🆕 Missing imports: {', '.join(missing_imports)}")
    elif custom_classes:
        print_manager.debug("✅ All custom classes already imported!")
        # Still continue to ensure format is correct
    
    # Define markers for our auto-generated sections
    import_marker_start = "# =============================================================================="
    import_header = "# Custom Class Imports (auto-generated)"
    import_tip = "# To add new classes: run cdf_to_plotbot('path/to/file.cdf') and this will be updated"
    import_marker_end = "# =============================================================================="
    
    all_marker_start = "# --- AUTO-GENERATED CUSTOM CLASS __ALL__ ENTRIES ---"
    all_marker_end = "# --- END AUTO-GENERATED __ALL__ ENTRIES ---"
    
    # Check which classes are already imported vs missing
    already_imported = []
    missing_classes = []
    
    for class_name in custom_classes:
        import_pattern = f"from .data_classes.custom_classes.{class_name} import"
        if import_pattern in content:
            already_imported.append(class_name)
        else:
            missing_classes.append(class_name)
    
    print_manager.debug(f"📊 Import status:")
    if already_imported:
        print_manager.debug(f"   ✅ Already imported: {', '.join(already_imported)}")
    if missing_classes:
        print_manager.debug(f"   🆕 Need to add: {', '.join(missing_classes)}")
    
    # Generate import section
    import_lines = [
        import_marker_start,
        import_header,
        import_tip,
        import_marker_start.replace("=", "-")  # Separator line
    ]
    
    for class_name in sorted(custom_classes):
        import_lines.append(f"from .data_classes.custom_classes.{class_name} import {class_name}, {class_name}_class")
    
    import_lines.extend([
        import_marker_start.replace("=", "-"),  # Separator line
        import_marker_end
    ])
    import_section = "\n".join(import_lines)
    
    # Generate __all__ entries
    all_lines = [all_marker_start]
    for class_name in sorted(custom_classes):
        all_lines.append(f"    '{class_name}',  # Custom generated class")
    all_lines.append(all_marker_end)
    all_section = "\n".join(all_lines)
    
    # Update imports section
    import_pattern = re.compile(
        rf'{re.escape(import_marker_start)}.*?{re.escape(import_marker_end)}',
        re.DOTALL
    )
    
    if import_pattern.search(content):
        # Replace existing section
        content = import_pattern.sub(import_section, content)
        print_manager.debug("📝 Updated existing custom imports section")
    else:
        # Find a good place to insert imports (after existing data class imports)
        insert_point = content.find("from .data_classes.psp_orbit import")
        if insert_point == -1:
            insert_point = content.find("# --- Explicitly Register Global Instances")
        
        if insert_point != -1:
            # Find the end of that line
            line_end = content.find('\n', insert_point)
            content = content[:line_end+1] + '\n' + import_section + '\n' + content[line_end+1:]
            print_manager.debug("📝 Added new custom imports section")
        else:
            print_manager.warning("❌ Could not find good insertion point for imports")
            return False
    
    # Update __all__ section
    all_pattern = re.compile(
        rf'{re.escape(all_marker_start)}.*?{re.escape(all_marker_end)}',
        re.DOTALL
    )
    
    if all_pattern.search(content):
        # Replace existing section
        content = all_pattern.sub(all_section, content)
        print_manager.debug("📝 Updated existing __all__ entries")
    else:
        # Find __all__ list and check for existing entries to avoid duplicates
        all_list_pattern = re.compile(r'(__all__\s*=\s*\[.*?)(])', re.DOTALL)
        match = all_list_pattern.search(content)
        
        if match:
            existing_all_content = match.group(1)
            
            # Check which custom classes are already in __all__ to avoid duplicates
            already_present = []
            missing_classes = []
            
            for class_name in custom_classes:
                if f"'{class_name}'" in existing_all_content:
                    already_present.append(class_name)
                else:
                    missing_classes.append(class_name)
            
            if already_present:
                print_manager.debug(f"📋 Already in __all__: {', '.join(already_present)}")
            
            if missing_classes:
                # Only add missing classes to avoid duplicates
                missing_entries = [f"    '{cls}',  # Custom generated class" for cls in sorted(missing_classes)]
                entries_to_add = '\n    ' + all_marker_start + '\n' + '\n'.join(missing_entries) + '\n    ' + all_marker_end
                
                new_all = existing_all_content + entries_to_add + '\n' + match.group(2)
                content = content[:match.start()] + new_all + content[match.end():]
                print_manager.debug(f"📝 Added {len(missing_classes)} missing custom classes to __all__ list")
            else:
                print_manager.debug("✅ All custom classes already present in __all__ list")
        else:
            print_manager.warning("❌ Could not find __all__ list to update")
            return False
    
    # Write updated content
    with open(init_file, 'w') as f:
        f.write(content)
    
    print_manager.status(f"✅ Successfully updated {init_file}")
    print_manager.status(f"🎉 Added {len(custom_classes)} custom classes to imports and __all__")
    return True

def validate_imports():
    """Validate that all custom classes can be imported."""
    script_dir = Path(__file__).parent
    plotbot_root = script_dir.parent if script_dir.name == 'scripts' else script_dir
    
    # Change to plotbot parent directory for import testing
    import sys
    sys.path.insert(0, str(plotbot_root.parent))
    
    try:
        import plotbot
        custom_classes_dir = plotbot_root / 'data_classes' / 'custom_classes'
        
        success_count = 0
        for py_file in custom_classes_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            class_name = py_file.stem
            if hasattr(plotbot, class_name):
                print_manager.debug(f"✅ {class_name} - Import successful")
                success_count += 1
            else:
                print_manager.warning(f"❌ {class_name} - Import failed")
        
        print_manager.status(f"🎯 Validation complete: {success_count} classes imported successfully")
        return success_count > 0
        
    except Exception as e:
        print_manager.error(f"❌ Validation failed: {e}")
        return False 