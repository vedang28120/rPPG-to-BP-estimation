# Data Module (`data/`)

## Purpose
Manages raw optical video recordings, serialized RGB pixel traces, resampled physiological arrays, and structured inference outputs.

## Dependencies
- External Libraries: `numpy`, `pandas`
- Internal Modules: Referenced by `core_extraction/`, `filtering/`, and `models/inference/`

## Key Files
- `raw/WIN_20260731_09_47_27_Pro.mp4`: Primary baseline test video of subject facial recording for rPPG benchmarking.
- `raw/rgb_trace_*.csv`: Raw spatial mean RGB color time-series logged directly from Android camera sensors.
- `processed/ppg_output.npy`: Standardized 125 Hz normalized single-channel BVP blood volume pulse array ready for model inference.
- `processed/ppg_output.csv`: Timestamped dataframe containing temporal index and normalized PPG waveforms.
- `processed/bp_predictions.csv`: Model output predictions containing window timestamps, estimated Systolic (SBP), and Diastolic (DBP) values.
- `processed/vitals_log_*.csv`: Multi-vital logs containing windowed Heart Rate (HR), HRV (RMSSD), Respiration Rate (RR), and Blood Pressure.
