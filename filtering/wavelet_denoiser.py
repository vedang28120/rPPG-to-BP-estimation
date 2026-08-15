"""
Wavelet Morphology Denoising Module
Implements Discrete Wavelet Transform (DWT) BayesShrink adaptive soft-thresholding for rPPG morphology preservation.
"""

import numpy as np
import pywt

def bayes_shrink_denoise(signal_data, wavelet='sym8'):
    """
    Suppresses dynamic camera sensor noise while retaining systolic peak inflection and dicrotic notch.
    
    Args:
        signal_data: 1D input array.
        wavelet: Wavelet family (default: 'sym8').
        
    Returns:
        Reconstructed denoised 1D waveform.
    """
    if len(signal_data) == 0:
        return signal_data
        
    coeffs = pywt.wavedec(signal_data, wavelet)
    
    # Estimate noise variance from highest frequency detail subband (cD1)
    cd1 = coeffs[-1]
    noise_sigma = np.median(np.abs(cd1 - np.median(cd1))) / 0.6745
    noise_var = noise_sigma ** 2
    
    denoised_coeffs = [coeffs[0]]  # Preserve approximation coefficients intact
    
    for cd in coeffs[1:]:
        if len(cd) == 0:
            denoised_coeffs.append(cd)
            continue
            
        subband_var = np.var(cd)
        sig_var = max(subband_var - noise_var, 0)
        
        if sig_var == 0:
            threshold = np.max(np.abs(cd))
        else:
            sig_std = np.sqrt(sig_var)
            threshold = noise_var / sig_std
            
        denoised = pywt.threshold(cd, value=threshold, mode='soft')
        denoised_coeffs.append(denoised)
        
    reconstructed = pywt.waverec(denoised_coeffs, wavelet)
    
    # Correct any boundary length discrepancies
    if len(reconstructed) > len(signal_data):
        reconstructed = reconstructed[:len(signal_data)]
    elif len(reconstructed) < len(signal_data):
        reconstructed = np.pad(reconstructed, (0, len(signal_data) - len(reconstructed)), 'edge')
        
    return reconstructed
