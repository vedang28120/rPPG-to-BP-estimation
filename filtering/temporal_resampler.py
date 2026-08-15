"""
Temporal Resampling Module
Converts Variable-Frame-Rate (VFR) timestamps to uniform 125 Hz sampling grids via PCHIP and Cubic Spline interpolation.
"""

import numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator

def resample_to_uniform_grid(timestamps_sec, signal_data, target_fs=125.0, method='cubic'):
    """
    Standardizes unevenly spaced camera traces onto a strict fixed-frequency time grid.
    
    Args:
        timestamps_sec: 1D array of monotonic timestamp values in seconds.
        signal_data: 1D or 2D array of signal samples.
        target_fs: Desired target sampling frequency (default: 125.0 Hz).
        method: 'cubic' (for continuous 2nd derivatives) or 'pchip' (for monotonicity preservation).
        
    Returns:
        uniform_time: 1D array of new equidistant timestamps.
        resampled_signal: Interpolated signal evaluated on uniform_time.
    """
    t = np.asarray(timestamps_sec)
    t_start, t_end = t[0], t[-1]
    duration = t_end - t_start
    if duration <= 0:
        raise ValueError("Invalid timestamp range: duration must be positive.")
        
    num_points = int(np.round(duration * target_fs))
    uniform_time = np.linspace(t_start, t_end, num_points)
    
    if method == 'pchip':
        interpolator = PchipInterpolator(t, signal_data, axis=0)
    else:
        interpolator = CubicSpline(t, signal_data, axis=0)
        
    resampled_signal = interpolator(uniform_time)
    return uniform_time, resampled_signal
