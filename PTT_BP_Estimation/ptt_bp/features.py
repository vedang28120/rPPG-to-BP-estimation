from __future__ import annotations

import numpy as np
import pandas as pd

from .timing import TimingResult


def timing_features(result: TimingResult, sample_rate_hz: float) -> dict[str, float]:
    values = result.timings_ms
    if len(values) == 0:
        raise ValueError(f"No valid {result.kind} matches")
    intervals = np.diff(result.reference_indices) / sample_rate_hz
    heart_rate = 60.0 / np.median(intervals) if len(intervals) else np.nan
    prefix = result.kind.lower()
    return {
        f"{prefix}_median_ms": float(np.median(values)),
        f"{prefix}_mean_ms": float(np.mean(values)),
        f"{prefix}_std_ms": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        f"inverse_{prefix}_per_s": float(1000.0 / np.median(values)),
        "valid_beats": float(len(values)),
        "heart_rate_bpm": float(heart_rate),
    }


def feature_frame(rows: list[dict[str, float | str]]) -> pd.DataFrame:
    return pd.DataFrame(rows)
