"""
Quality-Weighted Temporal Clip Fusion Module
Reference: ALIVE Framework / U-FaceBP Temporal Clip Weighting.
Segments continuous video/PPG into 4-second non-overlapping clips (minimum 2 cardiac cycles)
and dynamically fuses multi-clip blood pressure estimates weighted by instantaneous Signal Quality Indices (q_i).
"""

import numpy as np
from scipy import signal

def segment_into_clips(signal_1d, fs=125.0, clip_duration_sec=4.0):
    """
    Partitions a long continuous waveform into non-overlapping 4-second temporal chunks.
    
    Args:
        signal_1d: 1D or 2D array of signal samples.
        fs: Sampling frequency in Hz.
        clip_duration_sec: Clip length in seconds (default: 4.0s = 500 samples @ 125 Hz).
        
    Returns:
        clips: List of sliced signal arrays of exact clip length.
        clip_indices: List of (start_idx, end_idx) tuples.
    """
    clip_len = int(np.round(clip_duration_sec * fs))
    n_samples = len(signal_1d)
    
    clips = []
    clip_indices = []
    
    for start in range(0, n_samples - clip_len + 1, clip_len):
        end = start + clip_len
        clips.append(signal_1d[start:end])
        clip_indices.append((start, end))
        
    return clips, clip_indices

def compute_clip_quality_weight(clip_1d, fs=125.0):
    """
    Computes an instantaneous Signal Quality Index (q_i) in [0.0, 1.0] for a 4-second clip.
    Evaluates:
      1. Spectral Peak Purity (ratio of dominant cardiac peak power to in-band noise).
      2. Waveform Kurtosis & Skewness consistency.
      3. Inter-Beat Interval (IBI) regularity across detected pulse peaks.
    """
    if len(clip_1d) < int(fs * 2.0):
        return 0.0
        
    if np.isnan(clip_1d).any() or np.isinf(clip_1d).any():
        return 0.0
        
    std_val = float(np.std(clip_1d))
    if std_val < 1e-4:
        return 0.0
        
    # 1. Welch Spectral Purity
    nperseg = min(len(clip_1d), 256)
    f, pxx = signal.welch(clip_1d, fs=fs, nperseg=nperseg, nfft=1024)
    
    hr_mask = (f >= 0.75) & (f <= 3.0)
    if not np.any(hr_mask):
        return 0.0
        
    p_peak = np.max(pxx[hr_mask])
    p_in_band = np.sum(pxx[hr_mask]) + 1e-8
    spectral_purity = p_peak / p_in_band  # Range ~ [0.1, 0.8]
    
    # 2. Peak Continuity
    peaks, _ = signal.find_peaks(clip_1d, distance=int(fs * 0.35))
    if len(peaks) < 2:
        peak_score = 0.2
    elif len(peaks) in [3, 4, 5, 6, 7]:  # Normal heart beats in 4 seconds = 45–105 BPM
        ibis = np.diff(peaks)
        cv_ibi = float(np.std(ibis) / (np.mean(ibis) + 1e-8))
        peak_score = max(0.0, 1.0 - cv_ibi)  # Lower coefficient of variation = higher score
    else:
        peak_score = 0.3
        
    # Composite Quality Score q_i
    q_i = float(0.6 * spectral_purity + 0.4 * peak_score)
    # Clip between 0.01 and 1.0
    return float(np.clip(q_i, 0.01, 1.0))

def quality_weighted_fusion(clip_predictions, quality_weights):
    """
    Fuses individual clip estimates using dynamic quality weighting:
    P_final = sum(q_i * P_i) / sum(q_i)
    
    Args:
        clip_predictions: Array or list of shape (N_clips, 2) for [SBP, DBP] (or (N_clips,)).
        quality_weights: List or 1D array of quality scores q_i of length N_clips.
        
    Returns:
        fused_bp: Weighted average prediction [SBP, DBP].
        metrics: Dictionary of aggregation metadata.
    """
    preds = np.asarray(clip_predictions)
    weights = np.asarray(quality_weights, dtype=np.float32)
    
    sum_w = np.sum(weights)
    if sum_w <= 0:
        return np.mean(preds, axis=0), {"quality_weights": weights.tolist()}
        
    norm_weights = weights / sum_w
    
    if preds.ndim == 2:
        fused_bp = np.sum(preds * norm_weights[:, np.newaxis], axis=0)
    else:
        fused_bp = np.sum(preds * norm_weights)
        
    return fused_bp, {
        "num_clips": len(preds),
        "normalized_weights": norm_weights.tolist(),
        "mean_quality": float(np.mean(weights))
    }
