# Deep Learning Models Module (`models/`)

## Purpose
Houses neural network architectures (Bayesian U-FaceBP, ALIVE alignment, DRP/BBP-Net, MODEL-06), pre-trained checkpoint weights, cloud GPU training pipelines (Google Colab), and edge inference executors.

## Dependencies
- External Libraries: `torch`, `torch.nn`, `tensorflow` / `tf_keras`, `huggingface_hub`, `scikit-learn`, `numpy`, `scipy`
- Internal Modules: Consumes standardized waveforms and topological features from `filtering/` and data structures from `data/processed/`

## Key Files
- `architectures/`: Graph definitions for Bayesian MC Dropout ResNet, ALIVE cross-modal alignment encoders, 6xT DRP/BBP-Net transit models, and Scaled Sigmoid heads.
- `checkpoints/`: Serialized production and baseline model weights (`.pth`, `.h5`).
- `training/`: Cloud GPU training routines for Google Colab (`train_roadmap_cloud.py`, `master_roadmap_colab.ipynb`).
- `inference/`: Sliding-window inference executors for continuous BP estimation and edge deployment converters.
