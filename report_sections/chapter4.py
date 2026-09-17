"""
report_sections/chapter4.py
===========================
Chapter 04: Proposed Methodology & System Architecture (Tightly formatted equations)
"""

import docx
from docx.shared import Inches, Pt, RGBColor

def build_chapter4(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom, add_equation_block):
    add_heading_chapter(doc, "CHAPTER-04", "PROPOSED METHODOLOGY & SYSTEM ARCHITECTURE")
    
    add_body_p(doc, "This chapter describes the comprehensive architecture and mathematical formulation of LuminaBP, an end-to-end machine learning framework for non-invasive, continuous blood pressure estimation from facial video streams. Following rigorous Nature-style scientific methodology, each pipeline stage is structured around three essential elements: Module Design, Motivation, and Technical Advantages.")

    # ---------------------------------------------------------
    # 4.1 System Overview & Architectural Pipeline
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.1 System Overview & Architectural Pipeline")
    add_body_p(doc, "The LuminaBP computational pipeline translates raw optical camera frames into calibrated systolic and diastolic blood pressure predictions through seven modular processing stages. The complete workflow is illustrated in Figure 4.1 and specified in Table 4.1.")

    add_figure(doc, "results/figures/fig_pipeline_overview.png", "4.1", "End-to-End LuminaBP System Architecture: Showing video acquisition with exposure lock, MediaPipe multi-ROI tracking, POS chrominance projection, Savitzky-Golay signal conditioning, morphological feature extraction, and the decoupled MODEL-06-SepHead deep sequential neural network.", width_in=5.8)

    t41_headers = ["Pipeline Stage", "Module Name", "Primary Operation / Algorithm", "Output Dimension / Rate"]
    t41_rows = [
        ["Stage 1", "Hardware Ingestion", "Camera2 API Locked Acquisition (30 FPS, Fixed ISO/WB)", "RGB Frame Stream (1080p @ 30 Hz)"],
        ["Stage 2", "Facial Tracking", "MediaPipe 468-Point Mesh (Forehead + Bilateral Malar ROIs)", "Spatial Mean RGB Signals (3 × T)"],
        ["Stage 3", "rPPG Extraction", "Plane-Orthogonal-to-Skin (POS) Chrominance Projection", "Raw Blood Volume Pulse (1D @ 30 Hz)"],
        ["Stage 4", "Signal Conditioning", "Butterworth Bandpass (0.7–3.5 Hz) + Savitzky-Golay Filter", "Denoised BVP Waveform (1D @ 125 Hz)"],
        ["Stage 5", "Feature Engineering", "Morphological, Temporal, Spectral & HRV Metrics", "Engineered Feature Vector (38 Features)"],
        ["Stage 6", "Deep Neural Network", "MODEL-06-SepHead (1D ResNet + BiGRU + MHSA + SepHeads)", "Continuous SBP / DBP Estimates (mmHg)"],
        ["Stage 7", "Clinical Calibration", "1-Point Offset Adjustment + SNR Rejection Gating", "Calibrated Clinical Report (AAMI Graded)"]
    ]
    add_table_custom(doc, "4.1", "LuminaBP Multi-Stage Architectural Pipeline Specifications", t41_headers, t41_rows, col_widths=[1.0, 1.3, 2.5, 1.8], show_caption=True)

    # ---------------------------------------------------------
    # 4.2 Module 1: High-Stability Video Acquisition & Exposure Lock
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.2 Module 1: High-Stability Video Acquisition & Exposure Lock")
    add_heading_sub2(doc, "4.2.1 Module Design")
    add_body_p(doc, "The acquisition module interfaces directly with hardware image sensors via the Android Camera2 NDK/Java API. Crucially, standard automatic camera loops—including Auto-Exposure (AE), Auto-White-Balance (AWB), and Auto-Focus (AF)—are locked to fixed manual parameters immediately upon face detection. Video frames are captured in uncompressed YUV_420_888 format at a constant 30 frames per second with monotonic nanosecond hardware timestamping.")

    add_heading_sub2(doc, "4.2.2 Motivation")
    add_body_p(doc, "Under normal operating conditions, commercial smartphone cameras continuously adjust shutter speed and sensor gain in response to subtle subject motion or background lighting shifts. These sudden exposure jumps alter RGB intensity by 5% to 20%, which completely overwhelms the subtle 0.5% pulsatile physiological signal, injecting non-cardiac spectral spikes that destroy rPPG phase information.")

    add_heading_sub2(doc, "4.2.3 Technical Advantages")
    add_body_p(doc, "By enforcing hardware-level exposure and gain locking, the sensor noise floor is stabilized, ensuring that temporal intensity modulations directly reflect true subcutaneous capillary hemoglobin absorption rather than camera firmware compensations.")

    # ---------------------------------------------------------
    # 4.3 Module 2: Facial Mesh Landmarking & Dynamic Multi-ROI Tracking
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.3 Module 2: Facial Mesh Landmarking & Dynamic Multi-ROI Tracking")
    add_heading_sub2(doc, "4.3.1 Module Design")
    add_body_p(doc, "LuminaBP integrates the Google MediaPipe Face Mesh pipeline, generating 468 3D facial landmarks in real time. Rather than taking a coarse bounding box encompassing non-vascular regions (eyes, hair, lips), the system dynamically isolates three anatomically rich microvascular regions: the upper forehead (landmarks 10, 338, 297, 332, 284, 251, 389) and bilateral malar/cheek zones (left: 116, 123, 147, 187, 205; right: 345, 352, 376, 411, 425), as shown in Figure 4.2.")

    add_figure(doc, "results/figures/fig1_roi_wireframe.png", "4.2", "MediaPipe 468-Point Facial Mesh Wireframe: Highlighting anatomically optimized regions of interest across the upper forehead and bilateral malar (cheek) capillary beds on a clean publication-grade white background.", width_in=5.8)

    add_heading_sub2(doc, "4.3.2 Motivation")
    add_body_p(doc, "Facial micro-movements, eye blinking, and speech induce significant motion artifacts. Coarse facial bounding boxes include ocular and oral regions where non-pulsatile optical changes dominate. Dynamic landmark-guided ROI tracking maintains strict spatial registration on dense dermal capillary beds regardless of rigid head rotations.")

    add_heading_sub2(doc, "4.3.3 Technical Advantages")
    add_body_p(doc, "Spatial averaging across segmented facial polygons reduces uncorrelated sensor readout noise by a factor of √N (where N is the pixel count in the ROI), elevating the rPPG signal-to-noise ratio by more than 18 dB.")

    # ---------------------------------------------------------
    # 4.4 Module 3: Chrominance Projection (POS Algorithm)
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.4 Module 3: Chrominance Projection (POS Algorithm)")
    add_heading_sub2(doc, "4.4.1 Module Design")
    add_body_p(doc, "The Plane-Orthogonal-to-Skin (POS) algorithm projects temporally normalized RGB color signals c_n(t) = c(t) / μ_c onto a 2D plane orthogonal to the skin tone vector. The mathematical derivation proceeds through orthogonal projection components S_1(t) and S_2(t), synthesized into a scalar blood volume pulse BVP(t) as follows:")

    # Tightly formatted equation block without excessive spacing
    add_equation_block(doc, [
        "S_1(t) = G_n(t) - B_n(t)",
        "S_2(t) = G_n(t) + B_n(t) - 2 · R_n(t)",
        "BVP(t) = S_1(t) + [ σ(S_1) / σ(S_2) ] · S_2(t)"
    ])

    add_heading_sub2(doc, "4.4.2 Motivation")
    add_body_p(doc, "Skin tone variations and specular surface glare introduce severe distortion in single-channel RGB traces. POS establishes a mathematically rigorous coordinate transformation that isolates intensity variations caused by hemoglobin absorption from specular reflections.")

    add_heading_sub2(doc, "4.4.3 Technical Advantages")
    add_body_p(doc, "Unlike data-driven Blind Source Separation (ICA), POS requires no matrix inversion or statistical convergence iterations, executing in O(1) time complexity with exceptional invariance to subject pigmentation and ambient lighting geometry.")

    # ---------------------------------------------------------
    # 4.5 Module 4: Multi-Stage Signal Conditioning & Savitzky-Golay Denoising
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.5 Module 4: Multi-Stage Signal Conditioning & Savitzky-Golay Denoising")
    add_heading_sub2(doc, "4.5.1 Module Design")
    add_body_p(doc, "Extracted rPPG signals undergo a three-stage conditioning pipeline (Figure 4.3):")
    add_bullet_p(doc, "Zero-Phase Butterworth Bandpass Filtering: A 4th-order forward-backward Butterworth filter with cutoff frequencies [0.7 Hz, 3.5 Hz] (corresponding to 42–210 BPM) eliminates low-frequency respiratory drift and high-frequency illumination flicker.", bold_prefix="1. ")
    add_bullet_p(doc, "Cubic Spline Upsampling: Upsamples the 30 Hz signal to 125 Hz to match clinical ECG/PPG standards and provide fine-grained temporal resolution.", bold_prefix="2. ")
    add_bullet_p(doc, "Adaptive Savitzky-Golay Polynomial Smoothing: Applies a 3rd-degree polynomial filter across a 15-point moving window to eliminate residual 8-bit quantization noise.", bold_prefix="3. ")

    add_figure(doc, "results/figures/fig2_signal_processing.png", "4.3", "Multi-Stage Signal Conditioning: Raw RGB traces (top), raw POS projection (middle), and final 125 Hz bandpass + Savitzky-Golay filtered Blood Volume Pulse waveform (bottom) preserving pulse peaks and dicrotic inflection.", width_in=5.8)

    add_heading_sub2(doc, "4.5.2 Motivation")
    add_body_p(doc, "Standard low-pass filters blur sharp physiological transitions and flatten inflection points. Because blood pressure correlates strongly with pulse wave derivative slopes and dicrotic inflection timings, preserving waveform shape without phase distortion is essential.")

    add_heading_sub2(doc, "4.5.3 Technical Advantages")
    add_body_p(doc, "Savitzky-Golay filtering preserves higher-order derivatives (velocity plethysmogram VPG and acceleration plethysmogram APG), ensuring that deep learning models receive clean, morphologically intact physiological inputs.")

    # ---------------------------------------------------------
    # 4.6 Module 5: Hemodynamic & Morphological Feature Engineering
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.6 Module 5: Hemodynamic & Morphological Feature Engineering")
    add_heading_sub2(doc, "4.6.1 Module Design")
    add_body_p(doc, "From each 10-second conditioned pulse window, LuminaBP extracts 38 handcrafted physiological biomarkers categorized into four domains:")
    add_bullet_p(doc, "Temporal Features: Systolic rise time (t_r), diastolic decay time (t_d), total pulse duration (t_p), and systolic-to-diastolic ratio.", bold_prefix="1. ")
    add_bullet_p(doc, "Morphological & Derivative Features: Augmentation Index (AIx = P_2 / P_1), Stiffness Index (SI = Body_Height / ΔT_{Dvp}), inflection area ratios, and APG wave ratios (b/a, c/a, d/a, e/a).", bold_prefix="2. ")
    add_bullet_p(doc, "Spectral Features: Dominant cardiac frequency, spectral energy distribution, spectral centroid, and spectral entropy.", bold_prefix="3. ")
    add_bullet_p(doc, "Heart Rate Variability (HRV) Features: Mean Inter-Beat Interval (IBI), Standard Deviation of NN intervals (SDNN), Root Mean Square of Successive Differences (RMSSD), and pNN50.", bold_prefix="4. ")

    add_heading_sub2(doc, "4.6.2 Motivation")
    add_body_p(doc, "Combining explicit hemodynamic features with raw deep learning embeddings provides inductive physical bias, stabilizing neural training and preventing spurious correlations.")

    add_heading_sub2(doc, "4.6.3 Technical Advantages")
    add_body_p(doc, "These features directly capture autonomic tone and vascular elasticity, providing explicit physiological anchors that correlate strongly with both SBP and DBP.")

    # ---------------------------------------------------------
    # 4.7 Module 6: Deep Sequential Architecture — MODEL-06-SepHead
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.7 Module 6: Deep Sequential Architecture — MODEL-06-SepHead")
    add_heading_sub2(doc, "4.7.1 Module Design")
    add_body_p(doc, "The deep learning core of LuminaBP is MODEL-06-SepHead (Figure 4.4), a hybrid multi-scale architecture comprising four specialized stages:")
    add_bullet_p(doc, "Multi-Scale 1D-ResNet Spatial Feature Extractor: Three parallel 1D convolutional branches with kernel sizes k ∈ {3, 7, 15} extract multi-resolution temporal features, followed by residual bottleneck layers.", bold_prefix="1. ")
    add_bullet_p(doc, "Bidirectional GRU Temporal Sequence Modeler: A 2-layer BiGRU with 128 hidden units captures forward and backward temporal pulse dynamics across the 10-second sequence.", bold_prefix="2. ")
    add_bullet_p(doc, "Multi-Head Self-Attention (MHSA): A 4-head self-attention module (d_k = 32) models non-local dependencies between cardiac cycles.", bold_prefix="3. ")
    add_bullet_p(doc, "Decoupled SBP and DBP Regression Heads: The latent representation is split into two independent multi-layer perceptron (MLP) branches, each containing Dense(64) -> LayerNorm -> GELU -> Dropout(0.2) -> Dense(1) layers.", bold_prefix="4. ")

    add_figure(doc, "results/figures/fig_model06_architecture.png", "4.4", "MODEL-06-SepHead Deep Neural Network Architecture: Multi-scale 1D ResNet backbone, Bidirectional GRU, Multi-Head Self-Attention, and mathematically decoupled SBP and DBP regression heads.", width_in=5.8)

    add_heading_sub2(doc, "4.7.2 Motivation")
    add_body_p(doc, "In monolithic neural networks where a single shared dense layer outputs both [SBP, DBP], backpropagation gradients from SBP (which depends on ventricular inotropy) conflict with gradients from DBP (which depends on peripheral resistance). This causes the network to compromise on an intermediate average, inducing template collapse.")

    add_heading_sub2(doc, "4.7.3 Technical Advantages")
    add_body_p(doc, "Decoupled regression heads allow each output pathway to specialize its weight transformations according to distinct cardiovascular physical laws, eliminating gradient interference and boosting DBP correlation significantly.")

    # ---------------------------------------------------------
    # 4.8 Module 7: Calibration Strategy & Signal Quality Rejection
    # ---------------------------------------------------------
    add_heading_sub1(doc, "4.8 Module 7: Calibration Strategy & Signal Quality Rejection")
    add_heading_sub2(doc, "4.8.1 Module Design")
    add_body_p(doc, "LuminaBP incorporates a lightweight 1-point hydrostatic cuff calibration mechanism: during initial setup, a single baseline cuff measurement establishes subject-specific baseline offsets [ΔSBP, ΔDBP]. Furthermore, a Signal-to-Noise Ratio (SNR) gating module continuously computes pulse spectral power; windows with SNR < -2.5 dB are rejected as invalid motion-corrupted samples.")

    add_heading_sub2(doc, "4.8.2 Motivation")
    add_body_p(doc, "Arterial compliance varies between individuals based on age, sex, and vascular remodeling. Single-point calibration aligns the model’s baseline while preserving dynamic tracking of relative BP fluctuations.")

    add_heading_sub2(doc, "4.8.3 Technical Advantages")
    add_body_p(doc, "Calibration reduces absolute error offsets across diverse demographic cohorts without requiring retraining, ensuring robust out-of-the-box clinical utility.")
