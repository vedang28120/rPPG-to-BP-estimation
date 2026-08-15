# MCD Dataset Model Accuracy Benchmark Report

Evaluation of current rPPG POS extraction engine & LSTM Blood Pressure Model against MCD dataset ground truths.

### Prediction vs Actual Ground Truth

| Subject | Actual HR | Pred HR | HR Err | Actual SBP | Pred SBP | SBP Err | Actual DBP | Pred DBP | DBP Err | Actual MAP | Pred MAP |
|---------|-----------|---------|--------|------------|----------|---------|------------|----------|---------|------------|----------|
| Subject_1020 | 83.0 | 55.9 | 27.1 | 105.0 | 117.4 | 12.4 | 78.0 | 72.8 | 5.2 | 87.0 | 87.7 |
| Subject_1024 | 78.0 | 51.3 | 26.7 | 106.0 | 128.7 | 22.7 | 59.0 | 73.6 | 14.6 | 74.7 | 92.0 |
| Subject_1035 | 93.0 | 72.9 | 20.1 | 112.0 | 126.6 | 14.6 | 72.0 | 66.9 | 5.1 | 85.3 | 86.8 |

### Mean Absolute Errors (MAE)
- **Heart Rate MAE**: `24.63 BPM`
- **Systolic BP (SBP) MAE**: `16.57 mmHg`
- **Diastolic BP (DBP) MAE**: `8.30 mmHg`
