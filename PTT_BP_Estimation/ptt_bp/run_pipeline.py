from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from .config import PipelineConfig
from .data_loading import load_manifest
from .features import feature_frame, timing_features
from .preprocessing import preprocess
from .synchronization import synchronize
from .timing import extract_pat, extract_ptt


def build_features(manifest: str, config: PipelineConfig) -> pd.DataFrame:
    rows = []
    for record in load_manifest(manifest, config):
        times, streams = synchronize(record, config.target_rate_hz, config.max_resample_gap_ms)
        if times[-1] - times[0] < config.min_recording_seconds:
            raise ValueError(f"{record.record_id}: shorter than min_recording_seconds")
        streams = {
            name: preprocess(x, config.target_rate_hz,
                             config.ecg_bandpass_hz if name == "ecg" else config.bandpass_hz)
            for name, x in streams.items()
        }
        if record.mode == "ecg_ppg_pat":
            result = extract_pat(streams["ecg"], streams["ppg"], config.target_rate_hz, config.pat_range_ms)
        else:
            result = extract_ptt(streams["proximal_ppg"], streams["distal_ppg"], config.target_rate_hz, config.ptt_range_ms)
        if len(result.timings_ms) < config.min_beats:
            raise ValueError(f"{record.record_id}: only {len(result.timings_ms)} valid {result.kind} beats")
        row = {"record_id": record.record_id, "subject_id": record.subject_id, "mode": record.mode,
               "sbp": record.sbp, "dbp": record.dbp}
        row.update(timing_features(result, config.target_rate_hz))
        rows.append(row)
    return feature_frame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract validated PAT/PTT features.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    frame = build_features(args.manifest, PipelineConfig.from_json(args.config))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Wrote {len(frame)} validated records to {args.output}")


if __name__ == "__main__":
    main()
