"""
Multi-Patch Canonical Correlation Analysis (CCA) & Blind Source Separation (BSS)
Extracts spatially coherent cardiac rPPG components across multiple facial sub-patches,
canceling localized specular reflections, motion artifacts, and illumination gradients.
"""

import numpy as np
from sklearn.cross_decomposition import CCA
from sklearn.decomposition import FastICA

def extract_cca_rppg(patch_rgb_dict, fps=30.0):
    """
    Applies Canonical Correlation Analysis across spatial sub-patch pairs
    to extract maximally correlated physiological pulse signals.
    
    Args:
        patch_rgb_dict: Dictionary mapping patch names (e.g. 'forehead_left', 'left_cheek_right')
                        to temporal (T, 3) arrays of RGB traces.
        fps: Sampling rate in Hz.
        
    Returns:
        fused_rppg: 1D composite rPPG signal isolating coherent pulse oscillations.
        patch_correlations: Dictionary of canonical correlation scores per pair.
    """
    patch_keys = [k for k in patch_rgb_dict.keys() if '_' in k and len(patch_rgb_dict[k]) > 10]
    
    if len(patch_keys) < 2:
        # Fallback to single patch mean if not enough patches
        first_key = list(patch_rgb_dict.keys())[0]
        c = np.asarray(patch_rgb_dict[first_key])
        return (c[:, 1] - np.mean(c[:, 1])) / (np.std(c[:, 1]) + 1e-8), {}
        
    # Group patches into two spatial sets (Left facial side vs Right facial side)
    left_patches = [k for k in patch_keys if 'left' in k]
    right_patches = [k for k in patch_keys if 'right' in k]
    
    if not left_patches or not right_patches:
        # Split arbitrarily if names do not match
        mid = len(patch_keys) // 2
        left_patches = patch_keys[:mid]
        right_patches = patch_keys[mid:]
        
    x_mat = np.hstack([np.asarray(patch_rgb_dict[k]) for k in left_patches])
    y_mat = np.hstack([np.asarray(patch_rgb_dict[k]) for k in right_patches])
    
    # Detrend columns
    x_mat = x_mat - np.mean(x_mat, axis=0)
    y_mat = y_mat - np.mean(y_mat, axis=0)
    
    # Apply CCA to find linear combinations of Left and Right patches that maximize correlation
    n_components = min(3, x_mat.shape[1], y_mat.shape[1])
    cca = CCA(n_components=n_components, max_iter=500)
    
    try:
        x_c, y_c = cca.fit_transform(x_mat, y_mat)
        
        # Select canonical component with highest cardiac periodicity (0.75 - 3.0 Hz power)
        best_score = -1.0
        best_signal = x_c[:, 0]
        
        for i in range(n_components):
            comp = x_c[:, i] + y_c[:, i]
            # Fast spectral check
            fft_vals = np.abs(np.fft.rfft(comp))
            freqs = np.fft.rfftfreq(len(comp), d=1.0/fps)
            cardiac_mask = (freqs >= 0.75) & (freqs <= 3.0)
            
            if np.any(cardiac_mask):
                cardiac_power = np.max(fft_vals[cardiac_mask])
                total_power = np.sum(fft_vals) + 1e-8
                ratio = cardiac_power / total_power
                if ratio > best_score:
                    best_score = ratio
                    best_signal = comp
                    
        # Normalize
        fused_rppg = (best_signal - np.mean(best_signal)) / (np.std(best_signal) + 1e-8)
        return fused_rppg, {"cardiac_purity": float(best_score)}
        
    except Exception:
        # Fallback to green channel mean across all patches
        all_greens = [np.asarray(patch_rgb_dict[k])[:, 1] for k in patch_keys]
        mean_green = np.mean(all_greens, axis=0)
        norm_green = (mean_green - np.mean(mean_green)) / (np.std(mean_green) + 1e-8)
        return norm_green, {"fallback": True}

def extract_ica_bss_rppg(rgb_trace_Nx3, fps=30.0):
    """
    Applies FastICA Blind Source Separation on 3-channel (R, G, B) temporal traces.
    """
    ica = FastICA(n_components=3, random_state=42, max_iter=500)
    sources = ica.fit_transform(rgb_trace_Nx3)
    
    # Pick source with strongest periodicity in cardiac band
    best_source = sources[:, 0]
    best_snr = -1.0
    
    for i in range(3):
        comp = sources[:, i]
        fft_vals = np.abs(np.fft.rfft(comp))
        freqs = np.fft.rfftfreq(len(comp), d=1.0/fps)
        cardiac_mask = (freqs >= 0.75) & (freqs <= 3.0)
        if np.any(cardiac_mask):
            p_cardiac = np.max(fft_vals[cardiac_mask])
            p_noise = np.mean(fft_vals[~cardiac_mask]) + 1e-8
            snr = p_cardiac / p_noise
            if snr > best_snr:
                best_snr = snr
                best_source = comp
                
    return (best_source - np.mean(best_source)) / (np.std(best_source) + 1e-8)
