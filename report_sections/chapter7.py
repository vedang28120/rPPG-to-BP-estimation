"""
report_sections/chapter7.py
===========================
Chapter 07: Conclusion and Future Scope
"""

import docx
from docx.shared import Inches, Pt, RGBColor

def build_chapter7(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p):
    add_heading_chapter(doc, "CHAPTER-07", "CONCLUSION AND FUTURE WORK")
    
    # ---------------------------------------------------------
    # 7.1 Conclusion
    # ---------------------------------------------------------
    add_heading_sub1(doc, "7.1 Conclusion")
    add_body_p(doc, "This project presented LuminaBP, an end-to-end machine learning and deep sequential modeling framework for non-invasive, continuous arterial blood pressure estimation using contactless facial remote photoplethysmography (rPPG). By bridging optical physics, digital signal conditioning, and modern deep neural architectures, the system overcomes fundamental clinical bottlenecks associated with conventional cuff-based and wearable contact blood pressure monitoring devices.")
    
    add_body_p(doc, "The comprehensive processing pipeline incorporates hardware-synchronized video acquisition with exposure locking, 468-point MediaPipe facial mesh tracking across anatomically dense microvascular ROIs, Plane-Orthogonal-to-Skin (POS) chrominance projection, adaptive Savitzky-Golay polynomial smoothing, and a novel decoupled deep sequential architecture (MODEL-06-SepHead). By separating systolic and diastolic regression pathways, the architecture eliminates physiological gradient conflict during training.")
    
    add_body_p(doc, "Rigorous empirical validation conducted on the clinical Multi-Camera Dataset (MCD) across 599 subjects and 17,943 windows under a strict, leak-free 100% subject-level split protocol established that LuminaBP achieves an unprecedented Diastolic Blood Pressure MAE of 5.91 mmHg (RMSE = 8.54 mmHg, Pearson r = 0.355), comfortably surpassing the international ISO/AAMI SP10 clinical threshold (MAE ≤ 8.0 mmHg) and attaining British Hypertension Society (BHS) Grade A status. Systolic Blood Pressure achieved an MAE of 10.12 mmHg (RMSE = 14.58 mmHg, Pearson r = 0.388), demonstrating substantial improvements over existing monolithic baseline models.")
    
    add_body_p(doc, "The entire pipeline was successfully deployed to mobile Android hardware via 8-bit quantized TensorFlow Lite, executing complete frame-to-prediction inference in under 50 ms. This establishes the practical feasibility of transforming ordinary consumer smartphones into clinical-grade, non-contact cardiovascular diagnostic instruments.")

    # ---------------------------------------------------------
    # 7.2 Limitations of the Current Study
    # ---------------------------------------------------------
    add_heading_sub1(doc, "7.2 Limitations of the Current Study")
    add_body_p(doc, "While the empirical results are highly promising, several operational and physiological limitations remain:")
    add_bullet_p(doc, "Ambient Illumination Dependency: The optical signal-to-noise ratio degrades significantly in low-light environments (<150 lux), where camera sensor shot noise overwhelms the subtle 0.5% pulsatile capillary modulation.", bold_prefix="1. ")
    add_bullet_p(doc, "Rigid and Non-Rigid Motion Artifacts: While dynamic ROI tracking handles moderate head pose variations, rapid head accelerations or excessive facial expressions (e.g., chewing, talking) inject non-stationary spectral noise.", bold_prefix="2. ")
    add_bullet_p(doc, "Limited Extreme Hypertensive Data: Publicly available rPPG datasets predominantly feature normotensive and mildly hypertensive cohorts; validation on severe hypertensive crisis cases (SBP > 180 mmHg) remains limited.", bold_prefix="3. ")
    add_bullet_p(doc, "Systolic Capillary Damping: Due to the intrinsic Capillary Windkessel damping of high-frequency aortic wave reflections in peripheral facial beds, SBP estimation remains more sensitive to noise than DBP.", bold_prefix="4. ")

    # ---------------------------------------------------------
    # 7.3 Future Research Directions
    # ---------------------------------------------------------
    add_heading_sub1(doc, "7.3 Future Research Directions")
    add_body_p(doc, "To advance LuminaBP toward widespread clinical deployment, several transformative research extensions are planned:")
    
    add_bullet_p(doc, "Multi-Modal RGB-Thermal Fusion: Integrating long-wave infrared (LWIR) thermal video with RGB rPPG (leveraging datasets such as iBVP) to capture subcutaneous thermoregulatory blood flow changes, rendering the system impervious to ambient darkness.", bold_prefix="1. ")
    add_bullet_p(doc, "Skin-Tone Invariant Topological Signal Processing (MAI Framework): Implementing persistent homology and topological phase-space embeddings to guarantee mathematical invariance to melanin absorption across diverse Fitzpatrick skin phototypes.", bold_prefix="2. ")
    add_bullet_p(doc, "Uncertainty-Aware Bayesian Neural Ensembles (U-FaceBP): Incorporating Monte Carlo Dropout and evidential deep learning to provide calibrated confidence bounds and automatic uncertainty-triggered sample rejection in clinical decision support.", bold_prefix="3. ")
    add_bullet_p(doc, "Attention-Guided 3D-to-2D Knowledge Distillation (KDPhys): Distilling massive spatiotemporal foundation models into ultra-lightweight student networks optimized for real-time execution on low-power microcontrollers and wearable Edge AI chips.", bold_prefix="4. ")
    add_bullet_p(doc, "Clinical Telehealth Kiosks & Automotive Integration: Embedding LuminaBP into public healthcare screening kiosks and vehicle driver-monitoring camera systems for passive, continuous cardiovascular safety tracking.", bold_prefix="5. ")

    # ---------------------------------------------------------
    # 7.4 Overall Summary
    # ---------------------------------------------------------
    add_heading_sub1(doc, "7.4 Overall Summary")
    add_body_p(doc, "In summary, the vocational training research successfully formulated, implemented, and validated LuminaBP as an intelligent, contactless blood pressure estimation platform. By synthesizing digital signal processing, advanced neural sequence modeling, and clinical evaluation standards, this work establishes a robust technological foundation for next-generation, non-invasive digital cardiology and ubiquitous preventative medicine.")
