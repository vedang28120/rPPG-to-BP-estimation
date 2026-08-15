"""
Filtering & Signal Processing Package
Provides temporal resampling, dual-stream bandpass filtering, wavelet denoising,
detrending, topological MAI phase-space extraction, and quality-weighted clip fusion.
"""

from .temporal_resampler import resample_to_uniform_grid
from .dual_stream_filter import butter_bandpass_filter, normalize_zscore
from .wavelet_denoiser import bayes_shrink_denoise
from .detrending import detrend_smoothness_priors
from .sqi_validator import evaluate_window_sqi
from .topological_mai import takens_delay_embedding, extract_topological_features
from .temporal_clip_fusion import segment_into_clips, compute_clip_quality_weight, quality_weighted_fusion

__all__ = [
    "resample_to_uniform_grid",
    "butter_bandpass_filter",
    "normalize_zscore",
    "bayes_shrink_denoise",
    "detrend_smoothness_priors",
    "evaluate_window_sqi",
    "takens_delay_embedding",
    "extract_topological_features",
    "segment_into_clips",
    "compute_clip_quality_weight",
    "quality_weighted_fusion"
]
