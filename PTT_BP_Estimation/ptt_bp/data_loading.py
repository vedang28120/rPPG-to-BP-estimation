from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import numpy as np
import pandas as pd


class UnsupportedTimingSourceError(ValueError):
    """Raised when a record cannot provide physiologically interpretable PTT/PAT."""


@dataclass
class Signal:
    timestamps_s: np.ndarray
    values: np.ndarray
    name: str


@dataclass
class Record:
    record_id: str
    subject_id: str
    mode: str
    signals: dict[str, Signal]
    sbp: float | None = None
    dbp: float | None = None


REQUIRED_SIGNALS = {
    "ecg_ppg_pat": {"ecg", "ppg"},
    "proximal_distal_ppg_ptt": {"proximal_ppg", "distal_ppg"},
}


def _read_signal(path: Path, name: str) -> Signal:
    frame = pd.read_csv(path)
    if not {"timestamp", "value"}.issubset(frame.columns):
        raise ValueError(f"{path}: expected timestamp,value columns")
    frame = frame[["timestamp", "value"]].dropna().sort_values("timestamp")
    time = frame["timestamp"].to_numpy(dtype=float)
    value = frame["value"].to_numpy(dtype=float)
    if len(time) < 4 or np.any(np.diff(time) <= 0):
        raise ValueError(f"{path}: timestamps must be strictly increasing with at least four samples")
    # Epoch-style values are conventionally milliseconds; retain second-scale recordings.
    if np.nanmedian(np.diff(time)) > 1.0:
        time = time / 1000.0
    return Signal(time, value, name)


def validate_manifest_entry(entry: dict[str, Any], config: Any) -> None:
    mode = entry.get("mode")
    if mode in config.rejected_modes:
        raise UnsupportedTimingSourceError(
            f"{entry.get('record_id', '<unknown>')}: {mode!r} is not a valid PTT/PAT timing source; "
            "facial ROI-to-ROI delay is explicitly unsupported."
        )
    if mode not in config.allowed_modes or mode not in REQUIRED_SIGNALS:
        raise UnsupportedTimingSourceError(f"Unsupported timing mode: {mode!r}")
    supplied = set(entry.get("signals", {}))
    missing = REQUIRED_SIGNALS[mode] - supplied
    if missing:
        raise ValueError(f"{entry.get('record_id', '<unknown>')}: missing signals {sorted(missing)}")
    synchronization = entry.get("synchronization")
    approved_methods = {"shared_hardware_clock", "verified_trigger"}
    if not isinstance(synchronization, dict) or synchronization.get("method") not in approved_methods:
        raise UnsupportedTimingSourceError(
            f"{entry.get('record_id', '<unknown>')}: timing sources must declare a validated "
            "shared_hardware_clock or verified_trigger synchronization method"
        )
    if not synchronization.get("validated", False):
        raise UnsupportedTimingSourceError(
            f"{entry.get('record_id', '<unknown>')}: synchronization is not marked validated"
        )


def load_manifest(path: str | Path, config: Any) -> list[Record]:
    manifest_path = Path(path).resolve()
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Manifest must be a JSON list of records")
    records: list[Record] = []
    for entry in entries:
        validate_manifest_entry(entry, config)
        signals = {
            name: _read_signal((manifest_path.parent / source).resolve(), name)
            for name, source in entry["signals"].items()
        }
        records.append(Record(str(entry["record_id"]), str(entry["subject_id"]), entry["mode"], signals,
                              entry.get("sbp"), entry.get("dbp")))
    return records
