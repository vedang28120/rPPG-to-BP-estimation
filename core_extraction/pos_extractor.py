"""
Plane-Orthogonal-to-Skin (POS) rPPG Algorithm
Reference: Wang, W., den Brinker, A. C., Stuijk, S., & de Haan, G. (2016).
Algorithmic Principles of Remote PPG. IEEE TBME.
"""

import numpy as np

def pos_algorithm(rgb_signal, fps, window_size=1.6):
    """
    Extracts pulsatile blood volume pulse (BVP) from RGB traces using POS projection.
    
    Args:
        rgb_signal: Array of shape (N, 3) representing [R, G, B] temporal traces.
        fps: Sampling rate (frames per second).
        window_size: Temporal sliding window in seconds (default 1.6s).
        
    Returns:
        h: Extracted 1D POS pulse waveform of length N.
    """
    n = len(rgb_signal)
    l = int(fps * window_size)
    if n < l:
        return np.zeros(n)
        
    h = np.zeros(n)
    count = np.zeros(n)
    
    for i in range(n - l + 1):
        window = rgb_signal[i:i+l]
        mean_c = np.mean(window, axis=0)
        mean_c[mean_c == 0] = 1e-5
        c_norm = window / mean_c
        
        r, g, b = c_norm[:, 0], c_norm[:, 1], c_norm[:, 2]
        
        # POS projection vectors
        x = g - b
        y = g + b - 2 * r
        
        std_x = np.std(x)
        std_y = np.std(y)
        alpha = std_x / std_y if std_y != 0 else 0
        
        s = x + alpha * y
        h[i:i+l] += s - np.mean(s)
        count[i:i+l] += 1
        
    count[count == 0] = 1
    return h / count
