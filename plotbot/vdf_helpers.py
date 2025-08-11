"""
plotbot/vdf_helpers.py

Pure helper functions for VDF-related computations that can be reused by
data classes and plotting code. Keep dependencies minimal (numpy only).
"""

from __future__ import annotations

import numpy as np
from typing import Tuple


def apply_zero_clipping(xlim: Tuple[float, float], ylim: Tuple[float, float],
                        x_max_bulk: float, y_max_bulk: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Apply intelligent zero clipping when bulk data doesn't cross zero.

    Clips upper bound to zero if data is entirely negative but padding pushed past zero.
    """
    x0, x1 = xlim
    y0, y1 = ylim

    if x_max_bulk < 0 and x1 > 0:
        x1 = 0.0
    if y_max_bulk < 0 and y1 > 0:
        y1 = 0.0

    return (x0, x1), (y0, y1)


def bulk_percentile_bounds(
    vx: np.ndarray,
    vy: np.ndarray,
    vdf_data: np.ndarray,
    percentile: float,
    x_padding: float,
    y_padding: float,
    enable_zero_clipping: bool = True,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Compute bounds around the bulk of VDF data using a percentile threshold.

    Returns (xlim, ylim) tuples.
    """
    # Find valid data points
    valid_mask = np.isfinite(vdf_data) & (vdf_data > 0)
    if not np.any(valid_mask):
        # Caller should decide fallback; return a neutral square
        return (-800.0, 0.0), (-400.0, 400.0)

    valid_vdf = vdf_data[valid_mask]
    vdf_threshold = np.percentile(valid_vdf, percentile)
    bulk_mask = vdf_data > vdf_threshold
    if not np.any(bulk_mask):
        bulk_mask = valid_mask

    vx_bulk = vx[bulk_mask]
    vy_bulk = vy[bulk_mask]

    x_min_bulk, x_max_bulk = np.min(vx_bulk), np.max(vx_bulk)
    y_min_bulk, y_max_bulk = np.min(vy_bulk), np.max(vy_bulk)

    xlim = (x_min_bulk - x_padding, x_max_bulk + x_padding)
    ylim = (y_min_bulk - y_padding, y_max_bulk + y_padding)

    if enable_zero_clipping:
        xlim, ylim = apply_zero_clipping(xlim, ylim, x_max_bulk, y_max_bulk)

    return xlim, ylim


def theta_square_bounds(
    vx_theta: np.ndarray,
    vz_theta: np.ndarray,
    padding: float,
    zero_center: bool = True,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Zero-centered, square bounds for the theta plane.

    Ensures Y-axis is symmetric around zero and X-axis is centered to contain data,
    with square aspect (same half-range) and additional padding.
    """
    vx_min, vx_max = np.nanmin(vx_theta), np.nanmax(vx_theta)
    vz_min, vz_max = np.nanmin(vz_theta), np.nanmax(vz_theta)

    vz_max_abs = max(abs(vz_min), abs(vz_max))
    y_half_range = vz_max_abs

    vx_center = (vx_max + vx_min) / 2.0
    vx_half_range = (vx_max - vx_min) / 2.0

    required_half_range = max(y_half_range, vx_half_range)
    final_half_range = required_half_range + padding

    xlim = (vx_center - final_half_range, vx_center + final_half_range)
    ylim = (-final_half_range, final_half_range) if zero_center else (
        -final_half_range + (vz_min + vz_max) / 2.0, final_half_range + (vz_min + vz_max) / 2.0
    )
    return xlim, ylim


def theta_smart_bounds(
    vx_theta: np.ndarray,
    vz_theta: np.ndarray,
    vdf_data: np.ndarray,
    percentile: float,
    padding: float,
    enable_zero_clipping: bool = True,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Smart square bounds for theta plane using bulk data percentile.
    
    Finds bulk data using percentile threshold, creates zero-centered Y axis,
    centers X axis on data, makes square aspect, and applies intelligent zero clipping.
    """
    # Find valid data points
    valid_mask = np.isfinite(vdf_data) & (vdf_data > 0)
    if not np.any(valid_mask):
        # Fallback to basic square bounds if no valid data
        return theta_square_bounds(vx_theta, vz_theta, padding, zero_center=True)

    # Find bulk data using percentile threshold
    valid_vdf = vdf_data[valid_mask]
    vdf_threshold = np.percentile(valid_vdf, percentile)
    bulk_mask = vdf_data > vdf_threshold
    
    if not np.any(bulk_mask):
        # If threshold too strict, fall back to valid data
        bulk_mask = valid_mask

    # Get bulk data extents
    vx_bulk = vx_theta[bulk_mask]
    vz_bulk = vz_theta[bulk_mask]
    
    vx_min_bulk, vx_max_bulk = np.min(vx_bulk), np.max(vx_bulk)
    vz_min_bulk, vz_max_bulk = np.min(vz_bulk), np.max(vz_bulk)

    # Calculate square bounds around bulk data
    vz_max_abs = max(abs(vz_min_bulk), abs(vz_max_bulk))
    y_half_range = vz_max_abs

    vx_center = (vx_max_bulk + vx_min_bulk) / 2.0
    vx_half_range = (vx_max_bulk - vx_min_bulk) / 2.0

    # Ensure square aspect with Y-axis zero-centered
    required_half_range = max(y_half_range, vx_half_range)
    final_half_range = required_half_range + padding

    xlim = (vx_center - final_half_range, vx_center + final_half_range)
    ylim = (-final_half_range, final_half_range)

    # Apply intelligent zero clipping for X-axis only (preserve Y symmetry)
    if enable_zero_clipping:
        xlim, ylim = apply_zero_clipping(xlim, ylim, vx_max_bulk, vz_max_bulk)
        # But preserve Y-axis symmetry for theta plane
        ylim = (-final_half_range, final_half_range)

    return xlim, ylim

