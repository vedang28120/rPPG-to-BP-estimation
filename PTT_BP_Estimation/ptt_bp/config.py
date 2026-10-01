from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class PipelineConfig:
    target_rate_hz: float = 125.0
    bandpass_hz: tuple[float, float] = (0.5, 8.0)
    ecg_bandpass_hz: tuple[float, float] = (5.0, 40.0)
    min_recording_seconds: float = 20.0
    min_beats: int = 12
    pat_range_ms: tuple[float, float] = (100.0, 450.0)
    ptt_range_ms: tuple[float, float] = (20.0, 300.0)
    max_resample_gap_ms: float = 100.0
    allowed_modes: tuple[str, ...] = ("ecg_ppg_pat", "proximal_distal_ppg_ptt")
    rejected_modes: tuple[str, ...] = ("facial_roi_pair", "single_rppg")

    @classmethod
    def from_json(cls, path: str | Path) -> "PipelineConfig":
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        for key in ("bandpass_hz", "ecg_bandpass_hz", "pat_range_ms", "ptt_range_ms", "allowed_modes", "rejected_modes"):
            if key in values:
                values[key] = tuple(values[key])
        config = cls(**values)
        for name, band in (("bandpass_hz", config.bandpass_hz), ("ecg_bandpass_hz", config.ecg_bandpass_hz)):
            if not (0 < band[0] < band[1] < config.target_rate_hz / 2):
                raise ValueError(f"{name} must lie below the Nyquist frequency")
        return config
