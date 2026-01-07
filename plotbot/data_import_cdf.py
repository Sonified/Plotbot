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


def _extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract date from CDF filename using common patterns.

    Supports patterns like:
    - hamstring_2020-01-29_v02.cdf (YYYY-MM-DD)
    - psp_fld_l2_mag_2021-04-29_v02.cdf
    - data_20210429_v01.cdf (YYYYMMDD)

    Returns:
        datetime object for the file's date, or None if no date found
    """
    # Try YYYY-MM-DD pattern first (most common)
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass

    # Try YYYYMMDD pattern
    match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass

    return None


def filter_cdf_files_by_time(file_paths: List[str], start_time: datetime, end_time: datetime) -> List[str]:
    """
    Filter CDF files by time range using cached metadata for lightning-fast filtering.

    OPTIMIZATION: First tries to extract date from filename (instant!), only falls back
    to opening CDF files if filename doesn't contain a date.

    Args:
        file_paths: List of CDF file paths to check
        start_time: Start of requested time range
        end_time: End of requested time range

    Returns:
        List of file paths that contain data in the requested time range
    """
    scanner = CDFMetadataScanner()
    relevant_files = []
    files_needing_scan = []

    print_manager.debug(f"🔍 Filtering {len(file_paths)} CDF files by time range")

    # PHASE 1: Fast filename-based filtering (no file I/O!)
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        file_date = _extract_date_from_filename(filename)

        if file_date:
            # For daily files, check if the file's date overlaps with requested range
            # File covers file_date 00:00:00 to file_date 23:59:59
            file_start = file_date
            file_end = datetime(file_date.year, file_date.month, file_date.day, 23, 59, 59)

            has_overlap = file_start <= end_time and file_end >= start_time

            if has_overlap:
                relevant_files.append(file_path)
                print_manager.debug(f"    ✅ {filename}: Date {file_date.strftime('%Y-%m-%d')} overlaps (filename match)")
            else:
                print_manager.debug(f"    ❌ {filename}: Date {file_date.strftime('%Y-%m-%d')} no overlap (filename match)")
        else:
            # No date in filename - need to scan the file
            files_needing_scan.append(file_path)

    if files_needing_scan:
        print_manager.debug(f"📂 {len(files_needing_scan)} files need metadata scan (no date in filename)")

    # PHASE 2: Scan files without dates in filename (fallback)
    for file_path in files_needing_scan:
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

    # CRITICAL: Sort files by date so the earliest file comes first
    # This ensures we load the file that contains data for the START of the requested trange
    def get_file_date(filepath):
        filename = os.path.basename(filepath)
        file_date = _extract_date_from_filename(filename)
        return file_date if file_date else datetime.max  # Put files without dates at the end

    relevant_files.sort(key=get_file_date)

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


def cdf_to_plotbot(file_path: str, class_name: Optional[str] = None, output_dir: Optional[str] = None) -> bool:
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
                   If None, auto-generates from CDF filename by stripping dates/versions
        output_dir: Directory to write files (default: plotbot/data_classes/custom_classes/)
        
    Returns:
        True if successful, False otherwise
    """
    # Auto-generate class name if not provided
    if class_name is None:
        class_name = _auto_generate_class_name(file_path)
        print_manager.status(f"🤖 Auto-generated class name: '{class_name}'")
    
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
                # Stash will auto-register the class type
                from .data_cubby import data_cubby
                data_cubby.stash(class_instance, class_name=class_name)
                
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
        
        # ✨ No need to update __init__.py - dynamic loading handles everything!
        print_manager.status(f"✅ Class will auto-load on next plotbot import - no __init__.py edits needed!")
        
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
    set_plot_config_code = []
    
    # Identify spectral variables for mesh creation
    spectral_vars = [var.name for var in metadata.variables if var.plot_type == 'spectral']
    
    # Helper function for spectral plot options with debugging
    def generate_spectral_plot_config_with_debug(var):
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
            plot_config=plot_config(
                data_type='{class_name}',
                var_name='{var.name}',
                class_name='{class_name}',
                subclass_name='{var.name}',
                plot_type='spectral',
                time=self.time if hasattr(self, 'time') else None,
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
            set_plot_config_code.append(generate_spectral_plot_config_with_debug(var))
        else:
            set_plot_config_code.append(f"""        self.{var.name} = plot_manager(
            self.raw_data['{var.name}'],
            plot_config=plot_config(
                data_type='{class_name}',
                var_name='{var.name}',
                class_name='{class_name}',
                subclass_name='{var.name}',
                plot_type='time_series',
                time=self.time if hasattr(self, 'time') else None,
                datetime_array=self.datetime_array,
                y_label='{var.y_label}',
                legend_label='{var.description}',
                color=None,
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
from plotbot.plot_config import plot_config, retrieve_plot_config_snapshot
from plotbot.time_utils import TimeRangeTracker
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
        object.__setattr__(self, 'time', None)
        object.__setattr__(self, '_current_operation_trange', None)
        {"object.__setattr__(self, 'variable_meshes', {})" if has_spectral else ""}
        
        # Store original CDF file path AND smart pattern for multi-file loading
        object.__setattr__(self, '_original_cdf_file_path', '{metadata.file_path}')
        object.__setattr__(self, '_cdf_file_pattern', '{generate_file_pattern_from_cdf(metadata.file_path, os.path.dirname(metadata.file_path))}')

        if imported_data is None:
            self.set_plot_config()
            print_manager.dependency_management("No data provided; initialized with empty attributes.")
        else:
            print_manager.dependency_management(f"Calculating {class_name} variables...")
            self.calculate_variables(imported_data)
            self.set_plot_config()
            print_manager.status(f"Successfully calculated {class_name} variables.")
        
        # NOTE: Registration with data_cubby is handled externally to avoid 
        # instance conflicts during merge operations (like mag_rtn classes)
    
    def update(self, imported_data, original_requested_trange=None):
        """Method to update class with new data."""
        # STYLE_PRESERVATION: Entry point
        print_manager.style_preservation(f"🔄 UPDATE_ENTRY for {{self.__class__.__name__}} (ID: {{id(self)}}) - operation_type: UPDATE")
        
        if original_requested_trange is not None:
            self._current_operation_trange = original_requested_trange
            print_manager.dependency_management(f"[{{self.__class__.__name__}}] Updated _current_operation_trange to: {{self._current_operation_trange}}")
        
        if imported_data is None:
            print_manager.datacubby(f"No data provided for {{self.__class__.__name__}} update.")
            return
        
        print_manager.datacubby("\\n=== Update Debug ===")
        print_manager.datacubby(f"Starting {{self.__class__.__name__}} update...")
        
        # STYLE_PRESERVATION: Before state preservation
        if hasattr(self, '__dict__'):
            from plotbot.plot_manager import plot_manager
            plot_managers = {{k: v for k, v in self.__dict__.items() if isinstance(v, plot_manager)}}
            print_manager.style_preservation(f"   📊 Existing plot_managers before preservation: {{list(plot_managers.keys())}}")
            for pm_name, pm_obj in plot_managers.items():
                if hasattr(pm_obj, '_plot_state'):
                    color = getattr(pm_obj._plot_state, 'color', 'Not Set')
                    legend_label = getattr(pm_obj._plot_state, 'legend_label', 'Not Set')
                    print_manager.style_preservation(f"   🎨 {{pm_name}}: color='{{color}}', legend_label='{{legend_label}}'")
                else:
                    print_manager.style_preservation(f"   ❌ {{pm_name}}: No _plot_state found")
        
        # Store current state before update (including any modified plot_config)
        current_plot_states = {{}}
        standard_components = {[var.name for var in metadata.variables]}
        
        # STYLE_PRESERVATION: During state save
        print_manager.style_preservation(f"💾 STATE_SAVE for {{self.__class__.__name__}} - capturing states for subclasses: {{standard_components}}")
        
        for comp_name in standard_components:
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager) and hasattr(manager, '_plot_state'):
                    current_plot_states[comp_name] = dict(manager._plot_state)
                    print_manager.datacubby(f"Stored {{comp_name}} state: {{retrieve_plot_config_snapshot(current_plot_states[comp_name])}}")
                    print_manager.style_preservation(f"   💾 Saved {{comp_name}}: color='{{current_plot_states[comp_name].get('color', 'Not Set')}}', legend_label='{{current_plot_states[comp_name].get('legend_label', 'Not Set')}}'")

        # Perform update
        # STYLE_PRESERVATION: After calculate_variables(), before set_plot_config()
        print_manager.style_preservation(f"🔄 PRE_SET_PLOT_CONFIG in {{self.__class__.__name__}} - about to recreate plot_managers")
        
        self.calculate_variables(imported_data)                                # Update raw data arrays
        print_manager.style_preservation(f"✅ RAW_DATA_UPDATED for {{self.__class__.__name__}} - calculate_variables() completed")
        
        self.set_plot_config()                                                  # Recreate plot managers for standard components
        print_manager.style_preservation(f"✅ PLOT_MANAGERS_RECREATED for {{self.__class__.__name__}} - set_plot_config() completed")
        
        # Ensure internal consistency after update (mirror mag_rtn pattern)
        self.ensure_internal_consistency()
        
        # Restore state (including any modified plot_config!)
        print_manager.datacubby("Restoring saved state...")
        
        # STYLE_PRESERVATION: During state restore
        print_manager.style_preservation(f"🔧 STATE_RESTORE for {{self.__class__.__name__}} - applying saved states to recreated plot_managers")
        
        for comp_name, state in current_plot_states.items():                    # Restore saved states
            if hasattr(self, comp_name):
                manager = getattr(self, comp_name)
                if isinstance(manager, plot_manager):
                    manager._plot_state.update(state)
                    for attr, value in state.items():
                        if hasattr(manager.plot_config, attr):
                            setattr(manager.plot_config, attr, value)
                    print_manager.datacubby(f"Restored {{comp_name}} state: {{retrieve_plot_config_snapshot(state)}}")
                    print_manager.style_preservation(f"   🔧 Restored {{comp_name}}: color='{{state.get('color', 'Not Set')}}', legend_label='{{state.get('legend_label', 'Not Set')}}'")
        
        # STYLE_PRESERVATION: Exit point - Final custom values confirmation
        print_manager.style_preservation(f"✅ UPDATE_EXIT for {{self.__class__.__name__}} - Final state verification:")
        if hasattr(self, '__dict__'):
            from plotbot.plot_manager import plot_manager
            final_plot_managers = {{k: v for k, v in self.__dict__.items() if isinstance(v, plot_manager)}}
            for pm_name, pm_obj in final_plot_managers.items():
                if hasattr(pm_obj, '_plot_state'):
                    color = getattr(pm_obj._plot_state, 'color', 'Not Set')
                    legend_label = getattr(pm_obj._plot_state, 'legend_label', 'Not Set')
                    print_manager.style_preservation(f"   🎨 FINAL {{pm_name}}: color='{{color}}', legend_label='{{legend_label}}'")
                    if color == 'Not Set' or legend_label == 'Not Set':
                        print_manager.style_preservation(f"   ⚠️  FINAL_STYLE_LOSS detected in {{pm_name}}!")
                else:
                    print_manager.style_preservation(f"   ❌ FINAL {{pm_name}}: No _plot_state found")
        
        print_manager.datacubby("=== End Update Debug ===\\n")
        
    def get_subclass(self, subclass_name):
        """Retrieve a specific component (subclass or property)."""
        print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] Attempting to get subclass/property: {{subclass_name}} for instance ID: {{id(self)}}")

        # First, check if it's a direct attribute/property of the instance
        if hasattr(self, subclass_name):
            # 🚀 PERFORMANCE FIX: Only set requested_trange on the SPECIFIC subclass being requested
            current_trange = TimeRangeTracker.get_current_trange()
            if current_trange:
                try:
                    attr_value = getattr(self, subclass_name)
                    if isinstance(attr_value, plot_manager):
                        attr_value.requested_trange = current_trange
                except Exception:
                    pass
            # Verify it's not a private or dunder attribute unless explicitly intended
            if not subclass_name.startswith('_'): 
                retrieved_attr = getattr(self, subclass_name)
                print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] Found '{{subclass_name}}' as a direct attribute/property. Type: {{type(retrieved_attr)}}")
                return retrieved_attr
            else:
                print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] '{{subclass_name}}' is an internal attribute, not returning via get_subclass.")
        
        # If not a direct attribute, check if it's a key in raw_data (original behavior for data components)
        if hasattr(self, 'raw_data') and self.raw_data and subclass_name in self.raw_data.keys():
            component = self.raw_data.get(subclass_name)
            print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] Found '{{subclass_name}}' as a key in raw_data. Type: {{type(component)}}. This might be raw data.")
            return component

        # If not found as a direct attribute or in raw_data keys
        print_manager.warning(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] '{{subclass_name}}' is not a recognized subclass, property, or raw_data key for instance ID: {{id(self)}}.")
        available_attrs = [attr for attr in dir(self) if not attr.startswith('_') and not callable(getattr(self, attr))]
        available_raw_keys = list(self.raw_data.keys()) if hasattr(self, 'raw_data') and self.raw_data else []
        print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] Available properties/attributes: {{available_attrs}}")
        print_manager.dependency_management(f"[{class_name.upper()}_CLASS_GET_SUBCLASS] Available raw_data keys: {{available_raw_keys}}")
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
        raise AttributeError(f"'{{self.__class__.__name__}}' object has no attribute '{{name}}'")
    
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
    
    def set_plot_config(self):
        """Set up plotting options for all variables"""
        dt_len = len(self.datetime_array) if hasattr(self, 'datetime_array') and self.datetime_array is not None else "None_or_NoAttr"
        print_manager.dependency_management(f"[CDF_CLASS_DEBUG] set_plot_config called for instance ID: {{id(self)}}. self.datetime_array len: {{dt_len}}")
        print_manager.dependency_management("Setting up plot options for {class_name} variables")
        
{chr(10).join(set_plot_config_code)}

    def ensure_internal_consistency(self):
        """Ensures .time and core data attributes are consistent with .datetime_array and .raw_data."""
        print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{{id(self)}} *** Called for {{self.class_name}}.{{self.subclass_name if self.subclass_name else 'MAIN'}}.")
        
        # Track what changed to avoid unnecessary operations
        changed_time = False
        changed_config = False
        
        # STEP 1: Reconstruct self.time from datetime_array (critical after merges)
        if hasattr(self, 'datetime_array') and self.datetime_array is not None:
            if len(self.datetime_array) > 0:
                new_time_array = self.datetime_array.astype('datetime64[ns]').astype(np.int64)
                if not hasattr(self, 'time') or self.time is None or not np.array_equal(self.time, new_time_array):
                    self.time = new_time_array
                    print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Updated self.time via direct int64 cast. New len: {{len(self.time)}}")
                    changed_time = True
            elif not hasattr(self, 'time') or self.time is None or (hasattr(self.time, '__len__') and len(self.time) != 0):
                self.time = np.array([], dtype=np.int64)
                print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Set self.time to empty int64 array (datetime_array was empty).")
                changed_time = True
        
        # STEP 2: Sync plot manager datetime references (existing logic)
        if hasattr(self, 'datetime_array') and self.datetime_array is not None and \\
           hasattr(self, 'raw_data') and self.raw_data:
            
            for var_name in self.raw_data.keys():
                if hasattr(self, var_name):
                    var_manager = getattr(self, var_name)
                    if hasattr(var_manager, 'plot_config') and hasattr(var_manager.plot_config, 'datetime_array'):
                        if var_manager.plot_config.datetime_array is None or \\
                           (hasattr(var_manager.plot_config.datetime_array, '__len__') and 
                            len(var_manager.plot_config.datetime_array) != len(self.datetime_array)):
                            var_manager.plot_config.datetime_array = self.datetime_array
                            print_manager.dependency_management(f"    [ENSURE_CONSISTENCY] Updated {{var_name}} plot_config.datetime_array")
                            changed_config = True
        
        # STEP 3: Only call set_plot_config if data structures actually changed
        if changed_time and hasattr(self, 'set_plot_config'):
            print_manager.dependency_management(f"    Calling self.set_plot_config() due to time reconstruction.")
            self.set_plot_config()
        
        # Log final state
        if changed_time or changed_config:
            print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{{id(self)}} *** CHANGES WERE MADE (time: {{changed_time}}, config: {{changed_config}}).")
        else:
            print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{{id(self)}} *** NO CHANGES MADE.")
        
        print_manager.dependency_management(f"*** ENSURE CONSISTENCY ID:{{id(self)}} *** Finished.")

    def restore_from_snapshot(self, snapshot_data):
        """Restore all relevant fields from a snapshot dictionary/object."""
        for key, value in snapshot_data.__dict__.items():
            object.__setattr__(self, key, value)

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
from plotbot.plot_config import plot_config

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
    def set_plot_config(self) -> None: ...
    def restore_from_snapshot(self, snapshot_data: Any) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __setattr__(self, name: str, value: Any) -> None: ...

# Instance
{class_name}: {class_name}_class
'''

    return pyi_code 


def _auto_generate_class_name(cdf_file_path: str) -> str:
    """
    Auto-generate a Python class name from a CDF filename by intelligently
    stripping dates, times, versions, and other variable elements.
    
    Args:
        cdf_file_path: Path to the CDF file
        
    Returns:
        Clean class name suitable for Python (lowercase, underscores)
        
    Examples:
        psp_fld_l2_mag_RTN_4_Sa_per_Cyc_20210807_v02.cdf → psp_fld_l2_mag_rtn_4_sa_per_cyc
        wi_elpd_3dp_20220602_v02.cdf → wi_elpd_3dp
        mms1_fpi_brst_l2_des-moms_20170802120000_v3.3.0.cdf → mms1_fpi_brst_l2_des_moms
    """
    import re
    
    # Get filename without extension
    filename = os.path.basename(cdf_file_path)
    name = filename.replace('.cdf', '').replace('.CDF', '')
    
    # Define aggressive patterns to strip dates/times/versions (order matters!)
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
        # Time patterns: HHMMSS, HHMM before version
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
    name = re.sub(r'[^a-z0-9_]', '_', name)  # Replace invalid chars with underscore
    name = re.sub(r'_+', '_', name)          # Clean up double underscores again
    name = name.strip('_')                   # Remove leading/trailing underscores
    
    return name


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

    # Trust the pattern we detected - no validation needed
    # The time filter will ensure we only load relevant files
    if replacements_made:
        print(f"  🎯 Generated file pattern: {pattern}")
        print(f"     This will match files with different dates/versions in: {os.path.dirname(cdf_file_path)}")
        print_manager.debug(f"  📝 Replaced: {', '.join(replacements_made)}")
    else:
        print(f"  📌 No date/version pattern detected, will only load: {pattern}")
        print(f"     Add more files with similar naming to enable multi-file loading")
    
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
# ✨ DEPRECATED: Auto-Init Updater (No longer needed!)
# Custom classes now load dynamically via _auto_register_custom_classes()
# in __init__.py - no manual editing required!
# ==============================================================================

# This entire section can be removed in future cleanup
# Keeping as comment for historical reference

def update_plotbot_init_DEPRECATED():
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