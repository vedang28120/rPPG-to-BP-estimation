# PTT/PAT Blood-Pressure Estimation

This is a separate research pipeline for timing-based blood-pressure estimation. It does **not** treat timing between two facial rPPG regions as pulse-transit time: facial ROI signals share the same camera clock, are too close for a reliable arterial path length, and their apparent phase offset can be created by extraction and filtering.

## Supported acquisition modes

| Mode | Required synchronous sources | Timing measured |
| --- | --- | --- |
| `ecg_ppg_pat` | ECG + a distal/contact PPG | ECG R-wave to PPG pulse foot (PAT) |
| `proximal_distal_ppg_ptt` | anatomically separated proximal and distal PPG sensors | proximal PPG foot to distal PPG foot (PTT) |

`facial_roi_pair` and `single_rppg` configurations are deliberately rejected. PAT includes pre-ejection period and must not be described as PTT.

## Existing-project data audit

`../data/raw/rgb_trace_*.csv` contains 15 facial RGB columns without timestamps or an independent timing reference. `../data/processed/vitals_log_*.csv` contains model outputs, not cuff labels synchronized to ECG/PPG. Those files are intentionally not consumed as PTT training data.

## Layout

- `ptt_bp/data_loading.py` – manifest and signal loading
- `ptt_bp/synchronization.py` – timestamp validation, overlap and common-rate resampling
- `ptt_bp/preprocessing.py` – physiological filtering and normalization
- `ptt_bp/timing.py` – R-wave/PPG-foot detection and PAT/PTT matching
- `ptt_bp/features.py` – robust timing and heart-rate features
- `ptt_bp/estimation.py` – calibration-aware BP model
- `ptt_bp/train.py`, `ptt_bp/evaluate.py`, `ptt_bp/run_pipeline.py` – command-line stages

## Input manifest

Pass a JSON list of records to the scripts. Each record has `record_id`, `subject_id`, `mode`, `signals`, `synchronization`, and optional cuff labels. Every signal CSV must have `timestamp` (seconds or milliseconds) and `value` columns. `signals` must contain `ecg` and `ppg` for PAT, or `proximal_ppg` and `distal_ppg` for PTT. `synchronization` must declare `{"method": "shared_hardware_clock", "validated": true}` or a validated trigger equivalent; independent device clocks are rejected. See `config/example_config.json` for thresholds and mode rules.

Example extraction (no BP estimation model required):

```powershell
python -m ptt_bp.run_pipeline --manifest path\\to\\manifest.json --config config\\example_config.json --output features.csv
```

Training requires cuff-aligned `sbp` and `dbp` fields and uses grouped subject splits where possible:

```powershell
python -m ptt_bp.train --manifest path\\to\\manifest.json --config config\\example_config.json --model-out artifacts\\ptt_bp.joblib
```

The pipeline records validation failures rather than silently estimating BP from invalid timing inputs. Research use only; it is not a medical device.
