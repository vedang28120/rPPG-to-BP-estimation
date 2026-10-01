from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.signal import find_peaks


@dataclass
class TimingResult:
    kind: str
    timings_ms: np.ndarray
    reference_indices: np.ndarray
    target_indices: np.ndarray


def _ppg_feet(ppg: np.ndarray, fs: float) -> np.ndarray:
    peaks, _ = find_peaks(ppg, distance=max(1, int(fs * 0.35)), prominence=0.25)
    feet: list[int] = []
    for peak in peaks:
        left = max(0, peak - int(fs * 0.7))
        foot = left + int(np.argmin(ppg[left:peak + 1]))
        if not feet or foot > feet[-1]:
            feet.append(foot)
    return np.asarray(feet, dtype=int)


def _next_in_range(reference: np.ndarray, targets: np.ndarray, fs: float, limits_ms: tuple[float, float]) -> tuple[np.ndarray, np.ndarray]:
    low, high = (int(v * fs / 1000.0) for v in limits_ms)
    kept_ref, kept_target = [], []
    for ref in reference:
        candidates = targets[(targets >= ref + low) & (targets <= ref + high)]
        if len(candidates):
            kept_ref.append(ref)
            kept_target.append(candidates[0])
    return np.asarray(kept_ref, dtype=int), np.asarray(kept_target, dtype=int)


def extract_pat(ecg: np.ndarray, ppg: np.ndarray, fs: float, limits_ms: tuple[float, float]) -> TimingResult:
    r_peaks, _ = find_peaks(ecg, distance=max(1, int(fs * 0.3)), prominence=0.5)
    refs, targets = _next_in_range(r_peaks, _ppg_feet(ppg, fs), fs, limits_ms)
    return TimingResult("PAT", (targets - refs) * 1000.0 / fs, refs, targets)


def extract_ptt(proximal_ppg: np.ndarray, distal_ppg: np.ndarray, fs: float, limits_ms: tuple[float, float]) -> TimingResult:
    refs, targets = _next_in_range(_ppg_feet(proximal_ppg, fs), _ppg_feet(distal_ppg, fs), fs, limits_ms)
    return TimingResult("PTT", (targets - refs) * 1000.0 / fs, refs, targets)
