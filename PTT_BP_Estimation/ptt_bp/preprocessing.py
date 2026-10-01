from __future__ import annotations

import numpy as np
from scipy.signal import butter, detrend, filtfilt


def preprocess(signal: np.ndarray, sample_rate_hz: float, bandpass_hz: tuple[float, float]) -> np.ndarray:
    if len(signal) < 24:
        raise ValueError("Signal too short for zero-phase filtering")
    low, high = bandpass_hz
    b, a = butter(3, [low, high], btype="bandpass", fs=sample_rate_hz)
    output = filtfilt(b, a, detrend(np.asarray(signal, dtype=float)))
    std = output.std()
    if not np.isfinite(std) or std == 0:
        raise ValueError("Signal has no usable variation")
    return (output - output.mean()) / std
