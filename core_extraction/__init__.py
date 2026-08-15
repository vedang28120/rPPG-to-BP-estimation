"""
Core Extraction Package
Provides dynamic face landmark tracking, multi-ROI color pooling, spatial sub-patch CCA,
rPPG subspace extractors, and optical anti-spoofing.
"""

from .face_mesh_tracker import extract_facial_rois, get_roi_bounding_box, ROI_LANDMARKS
from .pos_extractor import pos_algorithm
from .chrom_extractor import chrom_algorithm
from .green_extractor import green_algorithm
from .liveness_detector import calculate_ear, verify_liveness
from .multi_patch_cca import extract_cca_rppg, extract_ica_bss_rppg

__all__ = [
    "extract_facial_rois",
    "get_roi_bounding_box",
    "ROI_LANDMARKS",
    "pos_algorithm",
    "chrom_algorithm",
    "green_algorithm",
    "calculate_ear",
    "verify_liveness",
    "extract_cca_rppg",
    "extract_ica_bss_rppg"
]
