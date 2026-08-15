"""
Green-Channel rPPG Intensity Extractor
Extracts baseline blood volume pulse by isolating normalized Green channel fluctuations.
"""

import numpy as np

def green_algorithm(rgb_signal):
    """
    Extracts PPG waveform directly from normalized Green channel.
    """
    mean_c = np.mean(rgb_signal, axis=0)
    mean_c[mean_c == 0] = 1e-5
    g = rgb_signal[:, 1] / mean_c[1]
    # Invert so systolic peak is positive
    return -g
