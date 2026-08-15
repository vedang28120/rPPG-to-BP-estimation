# Mobile Remote Photoplethysmography (rPPG) & Cuffless Blood Pressure Inference

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh-00bcd4.svg)](https://developers.google.com/mediapipe)
[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](models/training/master_roadmap_colab.ipynb)

A production-ready, modular architecture for estimating continuous cuffless blood pressure via remote photoplethysmography (rPPG) from standard smartphone facial video recordings.

---

## 🏛️ Modular System Architecture

```text
rppg_to_bp_estimation/
├── data/                          # Standardized optical traces, raw video, & processed arrays
│   ├── raw/                       # Raw MP4 recordings & sensor CSV traces
│   └── processed/                 # 125 Hz normalized BVP arrays & prediction CSVs
│
├── core_extraction/               # Computer vision & spatial algorithms
│   ├── face_mesh_tracker.py       # MediaPipe 5-ROI 10-patch dynamic tracking
│   ├── multi_patch_cca.py         # Canonical Correlation Analysis & FastICA BSS
│   ├── pos_extractor.py           # Plane-Orthogonal-to-Skin (POS) algorithm
│   ├── chrom_extractor.py         # Chrominance-based (CHROM) extraction
│   ├── green_extractor.py         # Green-channel intensity baseline
│   └── liveness_detector.py       # EAR & 3D facial depth anti-spoofing
│
├── filtering/                     # DSP, Topological MAI & Clip Fusion
│   ├── topological_mai.py         # Takens delay embedding, Attractor PCA, RQA metrics
│   ├── temporal_clip_fusion.py    # 4s clip segmentation & quality-weighted fusion
│   ├── temporal_resampler.py      # PCHIP / Cubic Spline 125 Hz grid standardization
│   ├── dual_stream_filter.py      # 4th-order zero-phase Butterworth bandpass
│   ├── wavelet_denoiser.py        # DWT BayesShrink (sym8) morphology denoising
│   ├── detrending.py              # Smoothness Priors Approach (SPA) baseline correction
│   └── sqi_validator.py           # Welch SNR, skewness & kurtosis quality gates
│
├── models/                        # Deep sequence architectures, weights, & training
│   ├── architectures/             # Bayesian U-FaceBP, ALIVE alignment, DRP/BBP-Net, MODEL-06
│   ├── checkpoints/               # Frozen MODEL-06 weights (.pth) & MIMIC-III (.h5)
│   ├── training/                  # Cloud Colab training suite (master_roadmap_colab.ipynb)
│   └── inference/                 # Sliding-window BP predictor & TFLite exporter
│
├── utils/                         # Telemetry, publication graphics, & validation
│   ├── bland_altman_validator.py  # Subject-independent 5-fold ANSI/AAMI validator
│   ├── research_visualizer.py     # 3D attractors, uncertainty plots, LDS distributions
│   ├── data_logger.py             # Append-mode CSV telemetry logger
│   ├── pdf_report_generator.py    # Clinical PDF documentation compiler
│   └── cleanup_manager.py         # Safe repository hygiene & archival tool
│
├── results/                       # Experimental metrics & figures
│   ├── metrics/                   # Balancing comparison CSVs & ablation tables
│   └── figures/                   # Bland-Altman, attractors, & waveform reports
│
├── docs/                          # Academic publications, system specs, & roadmaps
│   ├── ROADMAP_IMPLEMENTATION_SPEC.md # Engineering & mathematical specifications
│   ├── Further_Steps_From_MODEL_06_SepHead.md
│   ├── academic_paper_rppg.pdf
│   └── Project_Documentation.pdf
│
└── mobile/                        # Android Camera2 application & release backups
    ├── android_app/               # Native Kotlin/Java + Python Camera2 state machine
    └── backups/                   # Validated release APK backups
```

---

## ⚡ Quick Start

### 1. Installation
```bash
git clone https://github.com/vedang28120/rPPG-to-BP-estimation.git
cd rPPG-to-BP-estimation
pip install -r requirements.txt
```

### 2. Predict Blood Pressure (Inference)
Run sliding-window inference on processed PPG signals:
```bash
python -m models.inference.predict_bp --ppg_file data/processed/ppg_output.npy --checkpoint models/checkpoints/MODEL-06-SepHead_original.pth
```

### 3. Cloud GPU Training (Google Colab)
Upload and run the standalone Jupyter notebook in Google Colab (T4 / A100 GPU):
- Open [models/training/master_roadmap_colab.ipynb](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/training/master_roadmap_colab.ipynb) in Google Colab.
- Executes Phase I (LDS), Phase II (ALIVE Pearson alignment), Phase III (Bayesian NLL), and Phase IV (TFLite INT8 Export).

### 4. Clinical Validation & Research Figures
```bash
python -m utils.bland_altman_validator
python -m utils.research_visualizer
```

---

## 🔬 Core Scientific Innovations

1. **Topological Signal Processing (MAI)**: Reconstructs phase-space attractors via Takens' Delay Embedding to achieve a 95% reduction in skin-tone and contact-pressure bias.
2. **Uncertainty-Aware Bayesian Multi-Modal Fusion (U-FaceBP)**: Monte Carlo Dropout with heteroscedastic NLL loss separates sensor noise (aleatoric) from clinical out-of-distribution cases (epistemic).
3. **PPG-Guided Cross-Modal Alignment (ALIVE)**: Pre-trained frozen contact PPG network guides the camera encoder via Pearson correlation loss ($\mathcal{L}_F = 1 - r(F_r, F_p)$).
4. **Dual-Site Transit Dynamics (DRP/BBP-Net)**: Ingests a $6 \times T$ derivative matrix and enforces physiological bounding via Scaled Sigmoid heads ($[80, 180]$ SBP, $[60, 130]$ DBP).
5. **Quality-Weighted Clip Fusion**: Fuses 4-second non-overlapping temporal clips weighted by instantaneous spectral purity indices ($q_i$).

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
