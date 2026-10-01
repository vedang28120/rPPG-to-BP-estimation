from __future__ import annotations

import numpy as np
from scipy.interpolate import PchipInterpolator

from .data_loading import Record, Signal


class SynchronizationError(ValueError):
    pass


def synchronize(record: Record, target_rate_hz: float, max_gap_ms: float) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Resample independent, timestamped sources to their common observed interval."""
    starts = [signal.timestamps_s[0] for signal in record.signals.values()]
    ends = [signal.timestamps_s[-1] for signal in record.signals.values()]
    start, end = max(starts), min(ends)
    if end <= start:
        raise SynchronizationError(f"{record.record_id}: no shared timestamp interval")
    grid = np.arange(start, end, 1.0 / target_rate_hz)
    if len(grid) < 4:
        raise SynchronizationError(f"{record.record_id}: overlapping recording is too short")
    resampled: dict[str, np.ndarray] = {}
    for name, signal in record.signals.items():
        gaps_ms = np.diff(signal.timestamps_s) * 1000.0
        if np.max(gaps_ms) > max_gap_ms:
            raise SynchronizationError(f"{record.record_id}/{name}: timestamp gap exceeds {max_gap_ms} ms")
        resampled[name] = PchipInterpolator(signal.timestamps_s, signal.values)(grid)
    return grid, resampled
