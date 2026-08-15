"""
Signal Quality Index (SQI) Validation Module
Computes spectral signal-to-noise ratio (SNR), skewness, kurtosis, and amplitude consistency to gate low-quality windows.
"""

import numpy as np
from scipy import signal, stats

def evaluate_window_sqi(window_data, fs=125.0, min_snr=2.0, max_skew=2.0, max_kurt=5.0):
    """
    Evaluates signal quality across morphological and spectral criteria.
    
    Args:
        window_data: 1D signal window.
        fs: Sampling rate in Hz.
        min_snr: Minimum allowable spectral SNR in dB (default: 2.0).
        max_skew: Maximum allowable skewness magnitude.
        max_kurt: Maximum allowable kurtosis value.
        
    Returns:
        is_valid: Boolean indicating whether window passes SQI criteria.
        metrics: Dictionary containing calculated SQI values.
    """
    if np.isnan(window_data).any() or np.isinf(window_data).any():
        return False, {"reason": "nan_inf"}
        
    std_val = float(np.std(window_data))
    if std_val < 1e-4:
        return False, {"reason": "flatline", "std": std_val}
        
    skew_val = float(stats.skew(window_data))
    kurt_val = float(stats.kurtosis(window_data))
    
    if abs(skew_val) > max_skew or kurt_val > max_kurt:
        return False, {
            "reason": "morphology_artifact",
            "skewness": skew_val,
            "kurtosis": kurt_val
        }
        
    # Welch spectral power estimation
    nperseg = min(len(window_data), 512)
    f, pxx = signal.welch(window_data, fs=fs, nperseg=nperseg, nfft=2048)
    
    hr_mask = (f >= 0.75) & (f <= 3.0)
    noise_mask = ~hr_mask
    
    p_signal = np.max(pxx[hr_mask]) if np.any(hr_mask) else 0.0
    p_noise = np.mean(pxx[noise_mask]) if np.any(noise_mask) else 1e-8
    if p_noise == 0:
        p_noise = 1e-8
        
    snr_db = 10.0 * np.log10(p_signal / p_noise)
    
    is_valid = snr_db >= min_snr
    return is_valid, {
        "passed": is_valid,
        "snr_db": float(snr_db),
        "skewness": skew_val,
        "kurtosis": kurt_val
    }
