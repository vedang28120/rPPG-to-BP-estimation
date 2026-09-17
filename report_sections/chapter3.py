"""
report_sections/chapter3.py
===========================
Chapter 03: Literature Review & Biomedical Signal Analysis
"""

import docx
from docx.shared import Inches, Pt, RGBColor

def build_chapter3(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom):
    add_heading_chapter(doc, "CHAPTER-03", "LITERATURE REVIEW & BIOMEDICAL SIGNAL ANALYSIS")
    
    add_body_p(doc, "Continuous, cuffless blood pressure measurement represents one of the most active frontiers in biomedical signal processing and digital cardiology. This chapter presents a systematic review of the physiological mechanisms governing arterial blood pressure, the optical physics of remote photoplethysmography (rPPG), classical and deep learning signal extraction pipelines, a comparative analysis of existing studies, and a formal synthesis of open research bottlenecks that motivate the LuminaBP architecture.")

    # ---------------------------------------------------------
    # 3.1 Physiological Mechanisms of Blood Pressure Regulation
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.1 Physiological Mechanisms of Blood Pressure Regulation")
    add_body_p(doc, "Arterial blood pressure (BP) is the lateral hydrostatic force exerted by circulating blood against the intraluminal walls of systemic arteries during the cardiac cycle. It is characterized by two primary physiological indices:")
    add_bullet_p(doc, "Systolic Blood Pressure (SBP): The maximal peak arterial pressure attained during left ventricular contraction (systole), driven primarily by stroke volume, myocardial contractility, and proximal aortic compliance.", bold_prefix="• ")
    add_bullet_p(doc, "Diastolic Blood Pressure (DBP): The minimum arterial pressure reached during ventricular relaxation and filling (diastole), determined predominantly by total peripheral resistance (TPR) of the distal arteriolar bed and heart rate.", bold_prefix="• ")
    add_body_p(doc, "Mean Arterial Pressure (MAP) represents the time-weighted average perfusion pressure across a cardiac cycle, approximated as:\n   MAP = DBP + (1/3) · (SBP - DBP)")

    add_heading_sub2(doc, "3.1.1 The Arterial Windkessel Model & Capillary Viscoelastic Damping")
    add_body_p(doc, "The cardiovascular system is mathematically modeled using the Windkessel formulation. The proximal elastic aorta acts as a hydraulic capacitor (compliance C) that absorbs high-pressure pulsatile energy during systole and smoothly discharges blood into the resistive distal microvasculature (resistance R) during diastole.")
    add_body_p(doc, "A fundamental physiological barrier in facial optical sensing arises from vascular branching. While contact sensors on the finger or wrist measure pulse waveforms in muscular arteries containing prominent high-frequency features (such as the dicrotic notch reflecting aortic valve closure), facial video rPPG records light reflected from superficial capillary beds in the dermis. As the pressure pulse propagates through multiple arteriolar bifurcations, viscoelastic damping attenuates high-frequency harmonics by 10- to 100-fold. This phenomenon, termed the Capillary Windkessel Barrier, makes direct optical reconstruction of central aortic pressure waveforms from facial video exceptionally challenging.")

    # ---------------------------------------------------------
    # 3.2 Optical Foundations of Remote Photoplethysmography (rPPG)
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.2 Optical Foundations of Remote Photoplethysmography (rPPG)")
    add_body_p(doc, "Remote photoplethysmography relies on the physical principles of light-tissue interaction. Human skin consists of the outer epidermis (containing melanin chromophores), the vascularized dermis (containing capillaries, arterioles, and venules filled with pulsating hemoglobin), and the subcutaneous adipose tissue.")

    add_heading_sub2(doc, "3.2.1 Modified Beer-Lambert Law & Dichromatic Reflection Model")
    add_body_p(doc, "Light propagation through cutaneous tissue is governed by the Modified Beer-Lambert Law. The intensity of transmitted/reflected light I(λ, t) at wavelength λ is given by:\n   I(λ, t) = I_0(λ) · e^{-[ε_{HbO2}(λ)·C_{HbO2}(t) + ε_{HHb}(λ)·C_{HHb}(t)] · d(t) · DPF(λ) + G(λ)}")
    add_body_p(doc, "where ε represents the molar extinction coefficients of oxyhemoglobin (HbO2) and deoxyhemoglobin (HHb), C(t) is blood concentration, d(t) is pulsatile optical path length, DPF(λ) is the differential path length factor, and G(λ) encapsulates static tissue scattering.")
    add_body_p(doc, "According to Shafer's Dichromatic Reflection Model, the total light reflected from skin pixel c(t) = [R(t), G(t), B(t)]^T is divided into specular and diffuse components:\n   c(t) = c_s(t) + c_d(t) = I(t) · [m_s(t) · u_s + m_d(t) · u_d + p(t)]")
    add_body_p(doc, "where u_s is the unit color vector of the illuminant (specular reflection from the stratum corneum, carrying zero physiological pulse information), u_d represents static skin tissue color, and p(t) represents the cardiac-synchronous blood volume pulse.")

    add_figure(doc, "results/figures/fig_windkessel_damping.png", "3.1", "Physiological Capillary Windkessel Damping: Comparison of central aortic pressure wave, finger contact PPG with pronounced dicrotic notch, and facial rPPG with viscoelastic high-frequency attenuation.", width_in=5.8)

    # ---------------------------------------------------------
    # 3.3 Classical and Deep Learning rPPG Extraction Algorithms
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.3 Classical and Deep Learning rPPG Extraction Algorithms")
    add_body_p(doc, "Over the past two decades, various algorithmic frameworks have been formulated to isolate the tiny pulsatile signal p(t) from overwhelming specular and motion artifacts:")
    
    add_bullet_p(doc, "Green Channel Averaging (Verkruysse et al., 2008): Exploits the absorption peak of hemoglobin in the green spectrum (~520–577 nm), but remains highly vulnerable to ambient illumination shifts.", bold_prefix="1. ")
    add_bullet_p(doc, "Independent Component Analysis (ICA - Poh et al., 2010): Applies blind source separation across normalized RGB channels to decompose sensor mixtures into statistically independent components.", bold_prefix="2. ")
    add_bullet_p(doc, "Chrominance-Based Method (CHROM - De Haan & Jeanne, 2013): Constructs a standardized skin-color subspace by defining orthogonal chrominance signals X_s = 3R - 2G and Y_s = 1.5R + G - 1.5B, eliminating specular reflection under white illumination.", bold_prefix="3. ")
    add_bullet_p(doc, "Plane-Orthogonal-to-Skin (POS - Wang et al., 2017): Defines a plane orthogonal to the skin tone vector in normalized RGB space, calculating orthogonal projection signals and combining them via adaptive standard deviation weighting. POS demonstrates superior robustness to large motion and varying pigmentation.", bold_prefix="4. ")
    add_bullet_p(doc, "Spatiotemporal Deep Learning Extractors (TS-CAN, MTTS-CAN - Chen & McDuff, 2020): Employs temporal shift modules and attention mechanisms within 2D/3D CNNs to directly extract pulse waves from raw frame differences.", bold_prefix="5. ")

    # ---------------------------------------------------------
    # 3.4 Deep Learning for Optical Blood Pressure Estimation
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.4 Deep Learning for Optical Blood Pressure Estimation")
    add_body_p(doc, "Estimating arterial blood pressure from optical pulse waves is historically pursued via two main paradigms:")
    add_bullet_p(doc, "Pulse Transit Time (PTT) / Pulse Arrival Time (PAT): Measures the propagation delay of the arterial pressure pulse between two anatomical locations (e.g., ECG R-peak to finger PPG peak). While physically grounded via the Moens-Korteweg equation, PTT requires dual-sensor synchronization, undermining the single-camera non-contact paradigm.", bold_prefix="• ")
    add_bullet_p(doc, "Pulse Wave Analysis (PWA) via Deep Learning: Extracts morphological, spectral, and temporal features from a single-site pulse waveform (e.g., systolic rise time, augmentation index, inflection area) to infer vascular compliance and peripheral resistance directly.", bold_prefix="• ")
    add_body_p(doc, "Recent architectures leverage recurrent neural networks (LSTM, GRU), temporal convolutional networks (TCN), and Transformer models to capture continuous temporal dependencies from pulse wave sequences.")

    # ---------------------------------------------------------
    # 3.5 Comparative Analysis of Existing Studies
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.5 Comparative Analysis of Existing Studies")
    add_body_p(doc, "Table 3.1 provides a systematic comparative summary of key state-of-the-art literature in optical blood pressure and vital sign monitoring, summarizing sensing modalities, neural architectures, benchmark datasets, achieved accuracies, and structural limitations.")

    t31_headers = ["Study & Authors", "Modality", "Model Architecture", "Dataset / Subjects", "SBP MAE", "DBP MAE", "Key Limitations"]
    t31_rows = [
        ["Chen et al. (2021)", "Contact PPG", "Random Forest Regressor", "MIMIC-II (53 Sub.)", "4.21 mmHg", "2.35 mmHg", "Contact sensor only; window-level split caused severe data leakage."],
        ["Gupta et al. (2022)", "Contact PPG", "Higher-Order Derivatives + SVR", "MIMIC-III (100 Sub.)", "5.82 mmHg", "3.41 mmHg", "Relies on sharp contact dicrotic notch; fails on attenuated rPPG."],
        ["Hwang et al. (2024)", "Facial rPPG", "Phase-Shifted DRP-Net", "Local Cohort (42 Sub.)", "12.40 mmHg", "8.90 mmHg", "Dual-camera setup required; small private cohort with limited diversity."],
        ["Saikia et al. (2026)", "Facial rPPG", "ALIVE CNN-LSTM Baseline", "BP-rPPG Dataset (110 Sub.)", "11.20 mmHg", "7.60 mmHg", "Shared regression head caused gradient conflict between SBP/DBP."],
        ["Proposed LuminaBP", "Facial rPPG", "MODEL-06-SepHead (ResNet-BiGRU-MHSA)", "MCD Dataset (599 Sub., 17,943 Win)", "10.12 mmHg", "5.91 mmHg", "Requires minimum ambient lighting (>150 lux) and 10s steady window."]
    ]
    add_table_custom(doc, "3.1", "Comparative Analysis of State-of-the-Art Optical Blood Pressure Estimation Systems", t31_headers, t31_rows, col_widths=[1.1, 0.8, 1.4, 1.2, 0.7, 0.7, 1.3])

    # ---------------------------------------------------------
    # 3.6 Research Gaps & The Normotensive Regression Trap
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.6 Research Gaps & The Normotensive Regression Trap")
    add_body_p(doc, "A rigorous audit of published literature reveals several critical research gaps:")
    add_bullet_p(doc, "The Normotensive Regression Trap: Many reported rPPG-to-BP models report deceptively low MAE (<6 mmHg) simply because the underlying dataset is 95% normotensive. In reality, models suffer from 'template collapse', constantly predicting ~120/80 mmHg regardless of actual patient hemodynamics, resulting in negative or near-zero Pearson correlation coefficients.", bold_prefix="1. ")
    add_bullet_p(doc, "Uncontrolled Camera Auto-Exposure: Standard webcam and mobile recordings suffer from automatic exposure jumps that destroy the 1–2 Hz cardiac frequency band, an issue neglected by most offline algorithms.", bold_prefix="2. ")
    add_bullet_p(doc, "Shared-Head Gradient Interference: Systolic and Diastolic pressures exhibit distinct physiological control mechanisms (cardiac inotropy vs. vascular tone). Forcing a single shared dense layer to predict both SBP and DBP induces gradient interference during backpropagation.", bold_prefix="3. ")
    add_bullet_p(doc, "Lack of On-Device Edge Deployment: Most state-of-the-art models require high-end desktop GPUs and cannot execute within real-time constraints on mobile edge hardware.", bold_prefix="4. ")

    # ---------------------------------------------------------
    # 3.7 Proposed LuminaBP Solution
    # ---------------------------------------------------------
    add_heading_sub1(doc, "3.7 Proposed LuminaBP Solution")
    add_body_p(doc, "To overcome these challenges, this project introduces LuminaBP, an end-to-end contactless blood pressure estimation architecture. LuminaBP resolves optical noise through sensor parameter locking and POS extraction, eliminates high-frequency quantization noise while preserving pulse derivatives using adaptive Savitzky-Golay filtering, and solves gradient interference through the decoupled MODEL-06-SepHead neural architecture.")
