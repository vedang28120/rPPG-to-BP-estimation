# MASTER\_PROJECT\_CONTEXT.md

## Definitive Technical Reference — Mobile rPPG to Cuffless Blood Pressure Estimation

> **Version**: 1.0  
> **Last Updated**: 2026-08-15  
> **Status**: Production Architecture — Post MODEL-06-SepHead Baseline Freeze  
> **Maintainer**: Vedang Bhatt  
> **Repository**: `vedang28120/rPPG-to-BP-estimation`

---

# 1. Executive Summary & Architecture Paradigm

## 1.1 What This Project Does

This codebase implements a **non-invasive, camera-only blood pressure estimation pipeline** that operates entirely on standard smartphone hardware. A user points their phone's front-facing camera at their face for approximately 7–10 seconds. The system:

1. Tracks the face via **468-point MediaPipe Face Mesh** landmarks.
2. Extracts spatial-mean RGB pixel intensities from three anatomical **Regions of Interest** (Forehead, Left Cheek, Right Cheek).
3. Applies the **Plane-Orthogonal-to-Skin (POS)** chrominance projection to cancel specular surface reflection and isolate the pulsatile hemoglobin absorption signal — the remote photoplethysmogram (**rPPG**).
4. Performs **dual-stream digital signal processing** (Butterworth bandpass for heart rate timing + BayesShrink wavelet denoising for waveform morphology preservation).
5. Feeds the cleaned, standardized, 125 Hz Blood Volume Pulse (**BVP**) waveform into a deep sequence model that maps temporal cardiovascular dynamics to continuous **Systolic Blood Pressure (SBP)** and **Diastolic Blood Pressure (DBP)** in mmHg.

## 1.2 The Architecture Paradigm: Record-then-Process

The mobile Android application is built on a **"Record-then-Process" asynchronous state machine** that fundamentally decouples optical data acquisition from computational inference:

```text
┌──────────────────────────────────────────────────────────────────────┐
│                    RECORD PHASE (Real-Time @ 30 FPS)                │
│                                                                      │
│  Camera2 API → YUV_420_888 → MediaPipe FaceMesh → RGB Spatial Mean  │
│  AE/AWB Convergence → Lock → Accumulate 7–10 sec RGB buffer         │
│                                                                      │
│  Constraints: No JNI bottleneck, no dropped frames, no GC pauses    │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ Buffer complete
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   PROCESS PHASE (Offline, Single-Shot)               │
│                                                                      │
│  VFR Correction → POS Extraction → Dual-Stream Filter → SQI Gate   │
│  → Derivative Tensor Construction → TFLite LSTM Inference           │
│  → SBP/DBP Estimation → Clinical Categorization                    │
└──────────────────────────────────────────────────────────────────────┘
```

**Why this matters**: Attempting real-time per-frame inference at 30 FPS on mobile hardware creates catastrophic **JNI (Java Native Interface) bottlenecks** — the Python/C++ DSP routines and TFLite interpreter cannot return within the 33 ms frame budget, causing frame drops that corrupt the temporal signal. By buffering the full recording window and processing it as a single batch *after* acquisition completes, the pipeline eliminates this constraint entirely.

## 1.3 The Dual-Model Architecture

The project maintains two parallel model lineages:

| Model | Framework | Training Data | Architecture | Status |
|:---|:---|:---|:---|:---|
| **Legacy LSTM** | TensorFlow/Keras → TFLite | MIMIC-III clinical waveforms | Multi-layer LSTM (875×1 input) | Deployed on Android; pretraining candidate |
| **MODEL-06-SepHead** | PyTorch | MCD-Iriun synchronized PPG | Dual-Branch 1D-ResNet + BiGRU + MHSA (1250×1 input) | Current best; server-side & Colab training |

The legacy LSTM is currently deployed on-device via TFLite. MODEL-06-SepHead is the research-side architecture being iteratively improved and is the intended replacement once domain transfer (PPG → rPPG) is validated.

---

# 2. Directory Map & Module Breakdown

```text
rppg_to_bp_estimation/
│
├── README.md                          # Repository overview & quick-start guide
├── MASTER_PROJECT_CONTEXT.md          # ← THIS FILE (Single Source of Truth)
├── LICENSE                            # MIT License
├── requirements.txt                   # Unified Python dependencies
├── .gitignore                         # Hardened security & binary protection
│
├── data/                              # §2.1 — Optical Data & Processed Arrays
│   ├── README.md
│   ├── raw/                           # Raw MP4 video, Android sensor CSV traces
│   └── processed/                     # 125 Hz .npy arrays, prediction CSVs, vitals logs
│
├── core_extraction/                   # §2.2 — Computer Vision & rPPG Algorithms
│   ├── README.md
│   ├── __init__.py
│   ├── face_mesh_tracker.py           # MediaPipe 468-point dynamic ROI bounding
│   ├── pos_extractor.py               # POS (Wang et al., 2016) chrominance projection
│   ├── chrom_extractor.py             # CHROM (de Haan & Jeanne, 2013) extraction
│   ├── green_extractor.py             # Green-channel intensity baseline
│   └── liveness_detector.py           # EAR blink dynamics + 3D depth anti-spoofing
│
├── filtering/                         # §2.3 — DSP & Physiological Denoising
│   ├── README.md
│   ├── __init__.py
│   ├── temporal_resampler.py          # PCHIP / Cubic Spline VFR → 125 Hz
│   ├── dual_stream_filter.py          # 4th-order zero-phase Butterworth bandpass
│   ├── wavelet_denoiser.py            # DWT BayesShrink (sym8) adaptive denoising
│   ├── detrending.py                  # Smoothness Priors Approach (SPA) baseline removal
│   └── sqi_validator.py              # Welch SNR, skewness, kurtosis quality gates
│
├── models/                            # §2.4 — Deep Learning Models
│   ├── README.md
│   ├── __init__.py
│   ├── architectures/                 # Network graph definitions
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── resnet_bigru_attn.py       # MODEL-06: Dual-Branch ResNet + BiGRU + MHSA
│   │   ├── demo_mlp.py               # MODEL-01: Demographics-only MLP baseline
│   │   └── legacy_lstm.py            # Legacy MIMIC-III pre-trained LSTM
│   ├── checkpoints/                   # Frozen model weights
│   │   ├── README.md
│   │   ├── MODEL-06-SepHead_original.pth
│   │   ├── MODEL-06-SepHead_balanced_moderate.pth
│   │   ├── MODEL-06-SepHead_balanced_strong.pth
│   │   └── lstm_ppg_nonmixed.h5
│   ├── training/                      # Training pipelines & Colab automation
│   │   ├── README.md
│   │   ├── train_bp_mcd.py            # Progressive ablation trainer (Phases 1–6)
│   │   ├── make_notebook.py           # .py → .ipynb compiler
│   │   └── train_bp_mcd_colab.ipynb   # GPU-ready Colab notebook
│   └── inference/                     # Prediction engines & edge converters
│       ├── README.md
│       ├── __init__.py
│       ├── predict_bp.py              # Sliding-window BP inference CLI
│       └── tflite_exporter.py         # Keras → TFLite quantized flatbuffer converter
│
├── utils/                             # §2.5 — Telemetry, Reporting & DevOps
│   ├── README.md
│   ├── __init__.py
│   ├── data_logger.py                 # Append-mode 13-column CSV telemetry logger
│   ├── research_visualizer.py         # IEEE/Nature publication plot generator
│   ├── pdf_report_generator.py        # Clinical PDF report compiler (fpdf2)
│   ├── cleanup_manager.py            # Repository hygiene & archival tool
│   └── plot_mae.py                    # MAE error distribution boxplots
│
├── results/                           # §2.6 — Experimental Benchmarks & Figures
│   ├── README.md
│   ├── metrics/                       # Balancing comparison CSVs, ablation tables
│   └── figures/                       # Bland-Altman, correlation, waveform reports
│
├── docs/                              # §2.7 — Academic Papers & Roadmaps
│   ├── README.md
│   ├── academic_paper_rppg.pdf        # rPPG & pulse wave velocity theory
│   ├── Project_Documentation.pdf      # Auto-generated system design report
│   └── Further_Steps_From_MODEL_06_SepHead.md  # 24-step Gold Progression roadmap
│
└── mobile/                            # §2.8 — Android Application & Deployment
    ├── README.md
    ├── android_app/                   # Camera2 Kotlin + Chaquopy Python + TFLite
    │   └── app/src/main/
    │       ├── java/com/rppg/bpestimation/
    │       │   ├── MainActivity.kt            # UI state machine & orchestration
    │       │   ├── CameraService.kt           # Camera2 AE/AWB Convergence-Hold-Lock
    │       │   ├── FaceLandmarkTracker.kt     # MediaPipe face mesh JNI bridge
    │       │   ├── BPInferenceEngine.kt       # TFLite LSTM interpreter singleton
    │       │   ├── OverlayView.kt             # Real-time wireframe canvas overlay
    │       │   └── HelpBottomSheetDialogFragment.kt
    │       ├── python/
    │       │   └── pos_engine.py              # Full DSP pipeline (POS + filters + vitals)
    │       └── assets/
    │           ├── face_landmarker.task        # MediaPipe face landmarker binary
    │           └── lstm_ppg_nonmixed.tflite   # On-device inference model
    └── backups/
        └── rPPG_BP_Estimation_Backup.apk      # Validated release build (307 MB)
```

---

# 3. The Mathematical & DSP Pipeline (Data Flow)

The end-to-end signal processing chain transforms raw camera photons into calibrated blood pressure estimates through six rigorously ordered stages:

```text
Stage 0         Stage 1           Stage 2          Stage 3
Camera      →   VFR Correction →  ROI Tracking  →  POS Extraction
(30 FPS VFR)    (125 Hz uniform)   (Face Mesh)      (Chrominance)

    Stage 4              Stage 5               Stage 6
→   Dual-Stream      →   Feature            →   Neural
    Filtering             Engineering            Inference
    (BPF + DWT)           (PPG, vPPG, aPPG)      (LSTM / ResNet)
```

## Stage 0: Hardware Optical State — AE/AWB Convergence-Hold-Lock

Before any optical data is scientifically valid, the camera sensor must reach **photometric steady state**. The Android Camera2 API is configured via `CameraService.kt` with a three-phase protocol:

1. **Convergence Phase**: Auto-Exposure (`CONTROL_AE_MODE_ON`) and Auto-White Balance (`CONTROL_AWB_MODE_AUTO`) are active. The ISP converges to stable gain and color temperature parameters for the ambient lighting and skin reflectance.
2. **Hold Phase**: The pipeline monitors `CaptureResult.CONTROL_AE_STATE` every frame. Data collection begins only after `AE_STATE_CONVERGED` is reported.
3. **Lock Phase**: Once converged, `CONTROL_AE_LOCK = true` and `CONTROL_AWB_LOCK = true` are set. This **freezes** the sensor ISO, shutter speed, and white balance gains. Additionally, `NOISE_REDUCTION_MODE_OFF`, `EDGE_MODE_OFF`, and `COLOR_CORRECTION_MODE_FAST` are enforced to prevent the ISP from applying dynamic filters that would corrupt the sub-pixel pulsatile signal.

**Frame rate** is hardware-locked to a strict `CONTROL_AE_TARGET_FPS_RANGE = Range(30, 30)`, requesting the sensor to deliver exactly 30 FPS. However, due to OS-level scheduling, GC pauses, and ISP pipeline stalls, the *actual delivered timestamps are variable* (VFR).

## Stage 1: Temporal Standardization — PCHIP / Cubic Spline Interpolation

Smartphone cameras deliver frames with **Variable Frame Rate (VFR)** jitter — actual inter-frame intervals fluctuate between 28–38 ms despite the 30 FPS target. If the signal is naively treated as uniform, all subsequent spectral analysis (HR extraction, filtering) produces frequency-shifted artifacts.

The `temporal_resampler.py` module corrects this:

$$\text{Given: } \{(t_i, \mathbf{C}_i)\}_{i=0}^{N-1} \text{ where } t_i \text{ are VFR timestamps and } \mathbf{C}_i \in \mathbb{R}^3 \text{ are RGB values}$$

$$\text{Compute: } \hat{\mathbf{C}}(t) = \text{PCHIP}(t) \text{ evaluated on uniform grid } t_k = k / f_s, \quad f_s = 125 \text{ Hz}$$

**Why PCHIP over Cubic Spline**: Standard cubic spline interpolation guarantees $C^2$ continuity (continuous second derivatives), which is desirable for computing the acceleration PPG (aPPG). However, it is prone to **Runge overshoot** — artificial inflections between data points that create phantom peaks in the BVP waveform. PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) enforces **monotonicity preservation**: if the original data is monotonically increasing between two points, the interpolant will not introduce a local extremum. This prevents the interpolator from hallucinating pulse inflections that do not exist in the original optical signal.

**Target**: 875 samples for the legacy LSTM (7 sec × 125 Hz) or 1250 samples for MODEL-06 (10 sec × 125 Hz).

## Stage 2: Region of Interest (ROI) Extraction & Spatial Averaging

The `face_mesh_tracker.py` module uses **MediaPipe Face Mesh** to track 468 3D facial landmarks in real-time. Three anatomical ROIs are defined by landmark index groups:

| ROI | MediaPipe Indices | Anatomical Region |
|:---|:---|:---|
| **Forehead** | `[10, 109, 151, 338]` | Upper central forehead (above glabella) |
| **Left Cheek** | `[116, 117, 118, 119]` | Left zygomatic / malar region |
| **Right Cheek** | `[345, 346, 347, 348]` | Right zygomatic / malar region |

For each ROI, the spatial mean of the enclosed RGB pixel patch is computed:

$$\bar{C}_{\text{ROI}}^{(c)}(t) = \frac{1}{|\Omega|} \sum_{(x,y) \in \Omega} I^{(c)}(x, y, t), \quad c \in \{R, G, B\}$$

The three ROI means are then averaged to produce a single composite RGB trace $\mathbf{C}(t) \in \mathbb{R}^3$ per frame. In the mobile pipeline, all 5 ROIs (3 standard + 2 additional cheek subdivisions) yield a 15-column RGB buffer that is passed to the Python `pos_engine.py`. For inference robustness, the **Central Forehead ROI** is used exclusively as the primary signal source, as it is least affected by facial hair, shadow occlusion, and bilateral asymmetric illumination.

## Stage 3: POS (Plane-Orthogonal-to-Skin) Chrominance Extraction

The raw RGB traces contain a mixture of three optical components:

1. **Pulsatile (AC)**: The desired hemoglobin absorption modulation caused by arterial blood volume changes during the cardiac cycle.
2. **Specular (DC)**: White surface reflections from the skin's stratum corneum — these are independent of wavelength and carry no physiological information.
3. **Motion artifacts**: Head movement causing spatial ROI drift.

The **POS algorithm** (Wang et al., IEEE TBME, 2016) implements `pos_extractor.py`:

```text
For each sliding window of L = ⌊fps × 1.6⌋ samples:
  1. Temporal normalization:  C̃ = C / mean(C)    (removes DC component)
  2. Chrominance projection:
       X = G̃ - B̃                               (skin-tone chroma difference)
       Y = G̃ + B̃ - 2R̃                          (specular reflection direction)
  3. Adaptive tuning:         α = σ(X) / σ(Y)   (data-driven combination weight)
  4. Signal extraction:       S = X + αY          (pulsatile projection)
  5. Overlap-add:             h[i:i+L] += S - mean(S)
```

The projection planes are chosen so that the specular reflection vector (equal-energy white light: $R = G = B$) lies in the **null space** of the projection, while the pulsatile hemoglobin absorption vector (differential absorption at 540 nm and 660 nm) is **maximally preserved**.

Alternative extractors available: **CHROM** (de Haan & Jeanne, 2013) via `chrom_extractor.py` and a simple **Green-channel** baseline via `green_extractor.py`.

## Stage 4: Dual-Stream Filtering

The raw POS signal contains both the desired cardiovascular waveform and residual noise from camera quantization, ambient light flicker, and motion. Two parallel filter paths are applied:

### Stream A — Heart Rate Isolation (Tight Band)

```text
4th-order Butterworth bandpass: [0.75, 3.0] Hz
Applied via scipy.signal.filtfilt (zero-phase, forward-backward)
→ Isolates fundamental HR frequency: 45–180 BPM
→ Used for: Welch PSD peak detection → HR, Pan-Tompkins IBI → HRV (RMSSD)
```

### Stream B — Morphology Preservation (Wide Band)

```text
1. BayesShrink Wavelet Denoising (sym8 wavelet, multi-level DWT):
   - Noise σ estimated from cD1 (highest-frequency detail):
     σ_noise = median(|cD1 - median(cD1)|) / 0.6745
   - Per-subband adaptive threshold:
     threshold = σ²_noise / σ_signal  (if signal variance > 0)
   - Soft thresholding preserves sub-threshold morphology

2. Smoothness Priors Approach (SPA) detrending (λ = 100):
   - Removes respiratory baseline wander (0.1–0.4 Hz) and vasomotor fluctuations
   - Formulated as: (I + λ²D₂ᵀD₂)z_trend = signal
   - Solved via sparse Cholesky factorization

3. Savitzky-Golay smoothing (window=21, polyorder=3):
   - Final high-frequency noise suppression without peak rounding
   - ~0.16 sec window at 125 Hz
```

**Why two streams**: The tight Butterworth bandpass in Stream A is excellent for spectral peak detection (HR) but **destroys the dicrotic notch and systolic upstroke morphology** — the exact features that encode blood pressure information. Stream B's wavelet pipeline preserves these features while removing only non-physiological noise.

### Signal Quality Index (SQI) Gate

Before any window proceeds to inference, `sqi_validator.py` enforces:
- **Flatline detection**: $\sigma < 10^{-4}$ → reject
- **Morphological artifacts**: $|\text{skewness}| > 2.0$ or $\text{kurtosis} > 5.0$ → reject
- **Spectral SNR**: Welch PSD peak-to-noise ratio in [0.75, 3.0] Hz band must exceed threshold
- **NaN/Inf/clipping**: Any non-finite values → reject

## Stage 5: Feature Engineering — The Spatial Derivative Tensor

The mobile pipeline (`pos_engine.py`) constructs a **3-channel morphology tensor** from Stream B output:

$$\text{PPG}(t) = \text{BVP}_{\text{morphology}}(t)$$

$$\text{vPPG}(t) = \frac{d}{dt}\text{PPG}(t) \approx \text{PPG}(t) - \text{PPG}(t-1)$$

$$\text{aPPG}(t) = \frac{d^2}{dt^2}\text{PPG}(t) \approx \text{vPPG}(t) - \text{vPPG}(t-1)$$

Each channel is independently **Z-score normalized** (zero mean, unit variance), then stacked:

$$\mathbf{X}(t) = \begin{bmatrix} \hat{\text{PPG}}(t) \\ \hat{\text{vPPG}}(t) \\ \hat{\text{aPPG}}(t) \end{bmatrix} \in \mathbb{R}^{3}$$

The final input tensor is shaped as `(1, 875, 3)` — one batch, 875 time steps (7 seconds at 125 Hz), 3 channels.

> **Important caveat**: The PPG/vPPG/aPPG derivative ablation experiment (`docs/Further_Steps_From_MODEL_06_SepHead.md`, §10) showed that derivatives **did not justify their inclusion** in the primary model. Numerical differentiation amplifies camera noise, and for eventual rPPG deployment, this is particularly dangerous. The current MODEL-06 training uses **PPG-only** (single channel) as the primary input. The multi-channel tensor remains available for the on-device legacy LSTM which was trained to expect 3-channel input.

## Stage 6: Neural Inference

See §4 below for full model architecture details.

---

# 4. Machine Learning & Inference Models

## 4.1 MODEL-06-SepHead (Current Best — PyTorch)

The primary research model is a **Dual-Branch 1D-ResNet + BiGRU + Multi-Head Self-Attention** architecture with decoupled SBP/DBP regression heads, implemented in `models/architectures/resnet_bigru_attn.py`:

```text
Input: (B, 1, 1250)  — 10-second window, single PPG channel, 125 Hz
         │
    ┌────┴────┐
    ▼         ▼
 Branch 1   Branch 2
 (k=5)      (k=11, dilated)
    │         │
 ResBlock    ResBlock        ← 3 × ResidualBlock1D each (32→64→128 channels)
 (stride=2)  (stride=2,        Batch normalization + ReLU + skip connections
              dilation=1,2,2)
    │         │
    └────┬────┘
         │
    Concatenate              ← (B, 256, L_down)
         │
    Permute (B, L, 256)
         │
    BiGRU (2-layer)          ← hidden=64, bidirectional → output=128
         │
    Multi-Head Self-Attention ← 4 heads, residual connection
         │
    Global Average Pooling   ← (B, 128)
         │
    [Optional] Demographic   ← MLP: demo_dim → 32
    Feature Fusion              Concatenate → (B, 160)
         │
    ┌────┴────┐
    ▼         ▼
 SBP Head  DBP Head          ← Separate: Linear(160→64) → ReLU → Dropout(0.2) → Linear(64→1)
    │         │
    ▼         ▼
   SBP       DBP              ← Continuous mmHg predictions
```

**Why dual branches**: Branch 1 (kernel\_size=5) captures sharp local morphological features (systolic peak slope, dicrotic notch). Branch 2 (kernel\_size=11, dilated) captures wider temporal patterns (pulse interval variability, respiratory modulation). Their concatenation gives the recurrent layers access to both scales simultaneously.

**Why separate heads**: SBP and DBP have fundamentally different physiological drivers. SBP is primarily determined by stroke volume and arterial compliance (systolic ejection), while DBP reflects peripheral vascular resistance (diastolic runoff). A single shared regression head forces the network to learn a compromise representation that underserves both targets. Separate heads allow each to specialize.

### Training Protocol

- **Dataset**: MCD-Iriun synchronized contact PPG recordings with cuff-validated SBP/DBP labels
- **Windowing**: 10-second windows (1250 samples), 50% overlap (625 sample step)
- **Split**: Subject-level `GroupShuffleSplit` — no subject appears in both train and test
- **Quality gate**: NaN/Inf, flatline ($\sigma < 10^{-4}$), amplitude range ($1.0 < \text{peak-to-peak} < 500.0$)
- **Hardware**: Google Colab T4/A100 GPU, batch size 128, cuDNN benchmark enabled, AMP FP16
- **Optimizer**: Adam with learning rate scheduling
- **Loss**: MSE with optional SBP/DBP weighting

### Current Performance (MODEL-06-SepHead\_original.pth)

| Metric | SBP | DBP |
|:---|---:|---:|
| **Window MAE** | 11.58 mmHg | 6.70 mmHg |
| **Window RMSE** | 14.58 mmHg | 8.54 mmHg |
| **Pearson r** | 0.388 | 0.355 |
| **Subject MAE** | **10.12 mmHg** | **5.91 mmHg** |

## 4.2 Legacy LSTM (On-Device — TensorFlow Lite)

The on-device inference model (`lstm_ppg_nonmixed.tflite`, loaded via `BPInferenceEngine.kt`):

- **Input shape**: `[1, 875, 3]` — 7-second window, 3 channels (PPG, vPPG, aPPG)
- **Architecture**: Multi-layer LSTM → Dense regression
- **Output**: Two separate tensors `[1, 1]` each — one for SBP, one for DBP
- **Training data**: MIMIC-III clinical waveform database (contact PPG, **not** camera rPPG)
- **Interpreter**: TFLite `Interpreter` with `runForMultipleInputsOutputs()` API
- **Post-processing**: `SBP = max(output_0, output_1)`, `DBP = min(output_0, output_1)` (physiological constraint enforcement)

## 4.3 Progressive Ablation Ladder

The training pipeline (`train_bp_mcd.py`) implements a 6-phase progressive ablation:

| Phase | Model | Description |
|:---|:---|:---|
| 1 | Baseline Lock | Verify no data leakage; freeze random seeds |
| 2 | MODEL-01 (DemoOnlyMLP) | Demographics-only MLP — population mean baseline |
| 3 | MODEL-03→06 | Architecture ladder: ResNet → +BiGRU → +MHSA → +DualBranch |
| 4 | Channel Ablation | PPG-only vs PPG+vPPG vs PPG+vPPG+aPPG |
| 5 | SBP Investigation | Separate heads, weighted loss |
| 6 | Balancing Experiments | Moderate vs. strong inverse-frequency sampling |

## 4.4 Calibration & Clinical Context

> **Critical limitation**: The current model produces **population-level relative estimates**, not absolute calibrated blood pressure. Without a single-point cuff calibration measurement to anchor the model's output to an individual's vascular physiology, predictions regress toward the population mean (~120/70 mmHg).

**Planned calibration protocol** (§19 of Gold Progression):
```text
Generic BP model + one cuff measurement → personal offset calibration → future BP estimates
```

---

# 5. Current Status, Known Problems & Hardware Limits

## 5.1 Current Stable State

```text
✓ MCD-Iriun synchronized contact PPG dataset integration
✓ Population mean baseline (DemoOnlyMLP)
✓ Demographic baseline
✓ 1D-ResNet baseline
✓ Dual-Branch ResNet + BiGRU
✓ Multi-Head Self-Attention (MHSA)
✓ Demographic feature fusion
✓ Separate SBP/DBP regression heads
✓ MODEL-06-SepHead_original = current best (frozen checkpoint)
✓ PPG / vPPG / aPPG derivative ablation (PPG-only selected)
✓ Moderate & strong subject-aware balancing experiments completed
✓ Android app with Camera2 AE/AWB lock, FaceMesh, and TFLite inference
✓ Modular codebase architecture with full context documentation
```

## 5.2 The Template Collapse Problem (Critical)

**Template Collapse** is the central unsolved challenge of this project. It manifests as the model predicting nearly identical SBP/DBP values for all subjects, collapsing toward the population mean.

### Root Cause Analysis

1. **The Windkessel Effect & Dicrotic Notch Attenuation**: In the arterial tree, the aorta and large arteries act as a **Windkessel** (elastic reservoir). The dicrotic notch — the brief pressure reversal caused by aortic valve closure — is the primary morphological feature that encodes diastolic pressure information. As the pressure wave propagates from the aorta to peripheral sites, arterial compliance progressively smooths this notch. By the time the pulse reaches the skin microvasculature (capillary bed), the dicrotic notch is **physically attenuated by 1–2 orders of magnitude** compared to a central arterial catheter waveform.

2. **Camera Quantization Floor**: Even if the dicrotic notch survives to the skin surface, the 8-bit RGB quantization of a consumer smartphone camera (256 intensity levels per channel) creates a **noise floor** of ~0.4% of the dynamic range. The pulsatile AC component of rPPG is typically only 0.1–2% of the DC signal. The dicrotic notch, being a sub-feature of this already-tiny AC component, frequently falls **below the sensor's quantization noise floor**.

3. **Nyquist Limit at 30 FPS**: The dicrotic notch occurs approximately 300 ms after the systolic peak and has a temporal width of ~30–60 ms. At 30 FPS (33 ms inter-frame interval), the notch spans roughly **1–2 samples** in the raw signal. After PCHIP interpolation to 125 Hz, these 1–2 original data points are "spread" across 4–8 interpolated samples, but **no new information is created** — the interpolator is merely constructing a smooth curve through the sparse original samples. The true Nyquist frequency of the raw 30 FPS signal is 15 Hz, which is sufficient for HR extraction (0.75–3.0 Hz) but marginal for morphological feature extraction.

4. **Regression to the Mean**: When the model cannot reliably extract discriminative morphological features, it minimizes its loss by predicting the expected value of the training distribution:
   - $\hat{\text{SBP}} \approx E[\text{SBP}] \approx 120 \text{ mmHg}$
   - $\hat{\text{DBP}} \approx E[\text{DBP}] \approx 70 \text{ mmHg}$
   
   This produces low *average* error (since most subjects are near the population mean) but **zero clinical utility** for detecting hypertension or hypotension.

### Diagnostic Evidence

The `balancing_comparison.csv` results show SBP MAE values of ~110 mmHg across all three balancing experiments — this indicates the model is predicting values that are systematically offset from ground truth, suggesting the absolute calibration anchor is missing or the domain gap between MCD-Iriun contact PPG and camera rPPG has not been bridged.

## 5.3 Known Engineering Constraints

| Constraint | Detail | Impact |
|:---|:---|:---|
| **30 FPS Hardware Ceiling** | Consumer smartphone cameras are locked to 30 FPS for front-facing sensors. Higher FPS requires hardware API bypass or specialized cameras. | Limits morphological temporal resolution; 15 Hz Nyquist. |
| **VFR Jitter** | Actual frame delivery varies ±5–8 ms from the 33 ms target due to OS scheduling, GC pauses, ISP delays. | Requires PCHIP resampling; introduces interpolation error. |
| **8-bit Quantization** | Camera sensor delivers 8-bit-per-channel RGB (256 levels). Industrial PPG sensors use 16–24 bit ADCs. | Dicrotic notch and small morphological features fall below noise floor. |
| **Memory Pressure** | `rPPG_BP_Estimation_Backup.apk` is 307 MB due to bundled TFLite model, MediaPipe task file, and Chaquopy Python runtime. | Limits deployment to devices with ≥4 GB RAM; cold start ~3–5 seconds. |
| **PPG → rPPG Domain Gap** | MODEL-06 is trained on **contact PPG** (MCD-Iriun finger/ear sensor), not camera rPPG. The model has never seen camera-derived waveforms during training. | Zero-shot camera inference may produce degraded accuracy; domain adaptation required. |
| **Single-Subject Calibration** | No per-user cuff calibration is implemented. All predictions are population-relative. | Predictions cluster around population mean; unusable for individual clinical decisions. |

## 5.4 Known Bugs & Warnings

- **Protobuf Runtime Version Conflict**: MediaPipe and TensorFlow ship conflicting `google.protobuf` runtime versions. The codebase includes a **monkey-patch shim** (`runtime_version` mock module) in several legacy scripts to suppress `ValidateProtobufRuntimeVersion` errors. This is fragile and should be replaced with proper dependency isolation.
- **Logcat Dump Size**: Device debug sessions generate logcat files exceeding 70 MB. These are now excluded by `.gitignore` but must be manually purged from local clones.
- **APK excluded from Git**: The 307 MB backup APK exceeds GitHub's 100 MB hard push limit. It is excluded via `.gitignore` and must be distributed via Google Drive or direct transfer.

---

# 6. Future Roadmap & Pivots

## 6.1 The Gold Progression (14-Step Experimental Roadmap)

From `docs/Further_Steps_From_MODEL_06_SepHead.md`:

```text
CURRENT: MODEL-06-SepHead_original (frozen)
     │
     ▼
 1.  BP distribution analysis (SBP/DBP histograms, percentiles)
 2.  Moderate subject-aware balancing → MODEL-06-SepHead_balanced_moderate
 3.  Strong balancing → MODEL-06-SepHead_balanced_strong
 4.  BP-bin MAE & bias evaluation across pressure ranges
 5.  Select best balanced candidate
     │
     ├────────────────────┐
     ▼                    ▼
 6.  Old LSTM test      7. MIMIC-III transfer learning
     (same protocol)       (pretrain encoder → fine-tune on MCD)
     │                    │
     └────────┬───────────┘
              ▼
 8.  Select best PPG model
 9.  External validation (CLBP-300 or compatible dataset)
10.  rPPG zero-shot test (PPG-trained model on camera waveforms)
11.  rPPG domain adaptation (frozen encoder → partial → full fine-tuning)
12.  Quality/uncertainty gating
13.  Single-point personal calibration
14.  TFLite/mobile quantization & deployment
```

## 6.2 Near-Term Engineering Pivots

| Priority | Pivot | Rationale |
|:---|:---|:---|
| **P0** | **PPG → rPPG Domain Transfer** | The current model has never seen camera-derived waveforms. This is the single most important experiment — if the PPG model does not survive transition to camera rPPG, the entire approach must be reconsidered. |
| **P1** | **Feature-Based XGBoost Exploration** | Extract handcrafted pulse wave features (systolic upstroke slope, pulse width, augmentation index, reflection index) and train a gradient-boosted tree. This provides an interpretable baseline and avoids the black-box failure mode of deep learning on noisy signals. |
| **P2** | **Explainable AI (XAI) with GradientSHAP** | Apply `captum.attr.GradientShap` to MODEL-06 to identify which temporal regions of the input waveform the model actually attends to. If the model ignores the dicrotic notch region entirely, this confirms the Template Collapse hypothesis and redirects engineering effort. |
| **P3** | **Higher FPS Hardware** | Explore devices with 60/120 FPS front camera capability (e.g., iPhone 15 Pro, Samsung S24 Ultra) or external USB cameras. Doubling the frame rate to 60 FPS raises the Nyquist limit to 30 Hz, potentially resolving the dicrotic notch undersampling problem. |
| **P4** | **MIMIC-III Encoder Pretraining** | Use the legacy MIMIC-III LSTM (`lstm_ppg_nonmixed.h5`) as a **pretraining initialization** for MODEL-06's encoder layers, then fine-tune on MCD-Iriun. This tests whether large-scale clinical PPG data provides transferable cardiovascular representations. |
| **P5** | **Personal Calibration System** | Implement a one-time cuff measurement flow that computes a per-user SBP/DBP offset, anchoring the model's relative predictions to absolute physiological values. |

## 6.3 Decision Framework

```text
Does the PPG-trained MODEL-06 survive zero-shot rPPG testing?
                    │
           ┌────────┴────────┐
          YES                NO
           │                  │
    Fine-tune on          Fundamental
    camera rPPG data      approach pivot:
           │              → Feature-based models
    Calibrate             → Higher FPS hardware
           │              → Contact PPG fallback
    Deploy on mobile
```

## 6.4 Architecture Complexity Moratorium

Per the Gold Progression guidelines (§18):

> **Do not add more architecture complexity yet.** Postpone: larger ResNet, Transformers, larger BiGRU, additional derivatives, more fusion blocks. The current architecture already provides meaningful improvement over simpler baselines. The next bottleneck must be determined experimentally, not assumed.

---

*End of MASTER\_PROJECT\_CONTEXT.md*
