# Model Inference Submodule (`models/inference/`)

## Purpose
Executes offline and real-time sliding-window blood pressure estimation on processed PPG signals and converts models for edge execution.

## Dependencies
- External Libraries: `torch`, `tensorflow`, `tf_keras`, `numpy`, `pandas`, `scipy`
- Internal Modules: Ingests files from `data/processed/` and loads weights from `models/checkpoints/`

## Key Files
- `predict_bp.py`: Production CLI runner that loads normalized 125 Hz PPG data, executes SQI filtering, runs forward inference, and calculates mean SBP/DBP with clinical risk categorization.
- `tflite_exporter.py`: Quantization and graph optimization pipeline to convert PyTorch / Keras weights into TensorFlow Lite flatbuffer files for Android integration.
