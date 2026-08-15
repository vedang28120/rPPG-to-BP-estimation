# Model Checkpoints Submodule (`models/checkpoints/`)

## Purpose
Stores frozen weight files, benchmark baselines, and ablation checkpoints for reproducible evaluation.

## Dependencies
- External Libraries: `torch`, `tensorflow`
- Internal Modules: Loaded by `models/inference/predict_bp.py` and `models/training/train_bp_mcd.py`

## Key Files
- `MODEL-06-SepHead_original.pth`: State-of-the-art dual-branch ResNet + BiGRU + MHSA model trained on natural MCD-Iriun distribution (SBP MAE: 11.58, DBP MAE: 6.70).
- `MODEL-06-SepHead_balanced_moderate.pth`: Checkpoint trained with moderate inverse-frequency subject-aware bin balancing.
- `MODEL-06-SepHead_balanced_strong.pth`: Checkpoint trained with strong bin equalization to combat regression-to-the-mean in extreme BP ranges.
- `lstm_ppg_nonmixed.h5`: Legacy Keras/TF model trained on MIMIC-III waveforms used for transfer learning and pretraining ablations.
