"""
Dual-Stream Physiological Bandpass Filtering
Applies zero-phase forward-backward Butterworth IIR filtering for heart rate band isolation.
"""

import numpy as np
from scipy import signal

def butter_bandpass_filter(data, lowcut=0.75, highcut=3.0, fs=125.0, order=4):
    """
    Applies forward-backward zero-phase 4th-order Butterworth bandpass filter.
    
    Args:
        data: 1D signal array.
        lowcut: Lower cutoff frequency (default 0.75 Hz = 45 BPM).
        highcut: Upper cutoff frequency (default 3.0 Hz = 180 BPM).
        fs: Sampling frequency in Hz.
        order: Filter order.
        
    Returns:
        Filtered 1D signal.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    padlen = min(150, len(data) - 1) if len(data) > 15 else 0
    return signal.filtfilt(b, a, data, padtype='odd', padlen=padlen)

def normalize_zscore(data, eps=1e-8):
    """
    Standardizes signal to zero mean and unit standard deviation.
    """
    mu = np.mean(data)
    sigma = np.std(data)
    return (data - mu) / (sigma + eps)
