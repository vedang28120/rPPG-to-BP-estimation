# Model Training Submodule (`models/training/`)

## Purpose
Implements end-to-end cloud training pipelines, Label Distribution Smoothing (LDS), Bayesian NLL loss optimization, ALIVE feature alignment, and automated Google Colab notebook generation supporting **both Google Cloud TPU (v5e-1) and NVIDIA GPUs (T4 / A100)**.

## Dependencies
- External Libraries: `torch`, `torch_xla` (optional for TPU), `huggingface_hub`, `scikit-learn`, `numpy`, `pandas`, `scipy`
- Internal Modules: Imports network definitions from `models/architectures/` and topological tools from `filtering/`

## Key Files
- `master_roadmap_colab.ipynb`: Ready-to-upload Google Colab notebook supporting 1-click cloud training on either **T4 GPU** (recommended for sequential 1D waveforms) or **TPU v5e-1** (PyTorch XLA optimized).
- `train_roadmap_cloud.py`: The complete 4-Phase cloud training suite executing Phase I (LDS inverse-frequency smoothing), Phase II (ALIVE Pearson alignment), Phase III (Bayesian heteroscedastic NLL), and Phase IV (KDPhys distillation) with the universal `HardwareAccelerator` abstraction.
- `make_roadmap_colab.py`: Compiler script that automatically packages all models, DSP routines, and training code into `master_roadmap_colab.ipynb`.
- `train_bp_mcd.py`: Baseline progressive ablation trainer (Phases 1–6).
- `make_notebook.py`: Baseline Colab notebook compiler.
- `train_bp_mcd_colab.ipynb`: Baseline Colab notebook.

## Hardware Accelerator Guide

| Accelerator | Best For | Characteristics |
|:---|:---|:---|
| **NVIDIA T4 GPU (Recommended)** | 1D Sequence Models (MODEL-06) | Zero XLA compilation overhead, native cuDNN BiGRU acceleration, instant ONNX/TFLite export. |
| **Google Cloud TPU v5e-1** | Large-scale Pretraining / Heavy 3D-CNNs | 197 TFLOPS BF16 matrix multiply units; requires fixed static batch shapes (`drop_last=True`) and PyTorch-XLA (`xm.optimizer_step`, `xm.mark_step`). |
