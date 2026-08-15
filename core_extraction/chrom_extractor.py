"""
Chrominance-based (CHROM) rPPG Algorithm
Reference: de Haan, G., & Jeanne, V. (2013). Robust pulse rate from chrominance-based rPPG. IEEE TBME.
"""

import numpy as np

def chrom_algorithm(rgb_signal, fps, window_size=1.6):
    """
    Extracts rPPG pulse waveform using chrominance difference signals.
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
        
        x = 3 * r - 2 * g
        y = 1.5 * r + g - 1.5 * b
        
        std_x = np.std(x)
        std_y = np.std(y)
        alpha = std_x / std_y if std_y != 0 else 0
        
        s = x - alpha * y
        h[i:i+l] += s - np.mean(s)
        count[i:i+l] += 1
        
    count[count == 0] = 1
    return h / count
