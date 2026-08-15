# Core Extraction Module (`core_extraction/`)

## Purpose
Performs real-time facial landmark detection, dynamic 5-ROI multi-patch bounding, spatial Canonical Correlation Analysis (CCA), chrominance subspace projections, and optical anti-spoofing verification.

## Dependencies
- External Libraries: `opencv-python` (`cv2`), `mediapipe`, `numpy`, `scikit-learn`
- Internal Modules: Ingests data from `data/raw/` and outputs spatial traces to `filtering/`

## Key Files
- `face_mesh_tracker.py`: Tracks 468 MediaPipe facial mesh landmarks and extracts dynamic spatial bounding boxes across 5 anatomical ROIs (Forehead, Left Cheek, Right Cheek, Nose, Chin) with 10 spatial sub-patches.
- `multi_patch_cca.py`: Implements Canonical Correlation Analysis (CCA) and Independent Component Analysis (FastICA) across left/right sub-patches to isolate cardiac-synchronous pulse waveforms.
- `pos_extractor.py`: Implements the Plane-Orthogonal-to-Skin (Wang et al., 2016) algorithm with temporal windowing and skin-vector projection to cancel specular reflection.
- `chrom_extractor.py`: Implements the Chrominance-based (Haan & Jeanne, 2013) rPPG extraction method using linear chrominance difference signals.
- `green_extractor.py`: Implements the Green-channel intensity variation baseline extractor for fast low-compute benchmarking.
- `liveness_detector.py`: Evaluates eye-aspect-ratio (EAR) blink dynamics and 3D facial mesh depth variance to reject 2D print and screen presentation attacks.
