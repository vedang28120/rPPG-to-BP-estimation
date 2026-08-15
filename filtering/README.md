# Filtering & Signal Processing Module (`filtering/`)

## Purpose
Standardizes temporal sampling rates, extracts topologically invariant phase-space features (MAI), executes dual-stream physiological filtering, and performs quality-weighted 4-second temporal clip fusion.

## Dependencies
- External Libraries: `numpy`, `scipy` (`signal`, `interpolate`, `sparse`), `pywt` (`PyWavelets`), `scikit-learn`
- Internal Modules: Consumes raw projections from `core_extraction/` and yields clean input tensors for `models/`

## Key Files
- `topological_mai.py`: Implements Takens' Delay Embedding Theorem, Attractor PCA, Recurrence Quantification Analysis (RQA), and SNR-adaptive scaling to achieve skin-tone and contact-pressure amplitude invariance.
- `temporal_clip_fusion.py`: Segments continuous rPPG waveforms into 4-second non-overlapping clips (minimum 2 cardiac cycles) and dynamically fuses predictions weighted by instantaneous Signal Quality Indices ($q_i$).
- `temporal_resampler.py`: Converts variable-frame-rate (VFR) optical timestamps to a strictly uniform 125 Hz grid using Piecewise Cubic Hermite Interpolating Polynomial (PCHIP) / Cubic Spline interpolation.
- `dual_stream_filter.py`: Executes split-path filtering: 4th-order zero-phase Butterworth bandpass (0.75–3.0 Hz) for HR peak timing, and wideband preservation for BP wave contouring.
- `wavelet_denoiser.py`: Performs discrete wavelet transform (DWT) multi-level decomposition with BayesShrink adaptive soft thresholding (`sym8`) to strip camera sensor noise while preserving dicrotic notch morphology.
- `detrending.py`: Applies the Smoothness Priors Approach (SPA) via sparse regularization matrices to remove low-frequency baseline wander caused by respiration or vasomotor fluctuations.
- `sqi_validator.py`: Computes Welch spectral signal-to-noise ratio (SNR), skewness, kurtosis, and clipping bounds to gate bad or motion-corrupted windows before neural inference.
