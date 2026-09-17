"""
report_sections/chapter1.py
===========================
Chapter 01: Introduction (Updated with detailed Scope Inclusions & Exclusions)
"""

import docx
from docx.shared import Inches, Pt, RGBColor

def build_chapter1(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_body_p, add_bullet_p):
    add_heading_chapter(doc, "CHAPTER-01", "INTRODUCTION")
    
    add_heading_sub1(doc, "1.1 Background and Clinical Context")
    add_body_p(doc, "Cardiovascular diseases (CVDs) remain the leading cause of global morbidity and mortality, claiming an estimated 17.9 million lives each year according to the World Health Organization (WHO). Hypertension—clinically defined as persistent systemic arterial blood pressure exceeding 130/80 mmHg—is the single most prevalent and modifiable risk factor for myocardial infarction, ischemic stroke, heart failure, chronic kidney disease, and cognitive decline. Globally, over 1.28 billion adults aged 30–79 are affected by hypertension, with approximately 46% unaware of their condition due to its largely asymptomatic nature during early stages. Consequently, frequent and continuous arterial blood pressure monitoring represents an indispensable clinical necessity for proactive diagnosis, therapeutic titration, and cardiovascular risk stratification.")
    
    add_body_p(doc, "For over a century, the standard of care for non-invasive arterial pressure measurement has relied on the pneumatic occlusive cuff, implemented via manual auscultatory sphygmomanometry or automated oscillometric cuffs. While clinically validated and widely standardized, cuff-based devices possess fundamental structural limitations that severely constrain their utility in modern preventive medicine:")
    
    add_bullet_p(doc, "Intermittent and Reactive Sampling: Cuff inflations take 30 to 60 seconds, providing only isolated, snapshot measurements that fail to capture rapid autonomic fluctuations, acute hypertensive spikes, or beat-to-beat hemodynamic dynamics.", bold_prefix="• ")
    add_bullet_p(doc, "Physical Disruption and Sleep Fragmentation: The repetitive mechanical inflation and deflation of an occlusive arm cuff causes cutaneous discomfort, localized vascular compression, and sleep disruption during ambulatory 24-hour monitoring, leading to poor patient compliance.", bold_prefix="• ")
    add_bullet_p(doc, "White-Coat and Masked Hypertension: The psychogenic stress of clinical cuff application frequently induces transient sympathetic arousal ('white-coat effect'), yielding artificially elevated readings, or conversely obscures nocturnal hypertension.", bold_prefix="• ")
    
    add_body_p(doc, "In response to these challenges, biomedical research has increasingly focused on cuffless optical modalities, predominantly contact photoplethysmography (cPPG). Embedded in consumer smartwatches and clinical pulse oximeters, cPPG illuminates tissue with light-emitting diodes (LEDs) and detects transmitted or backscattered light modulated by blood volume changes within the microvascular bed. However, contact wearables introduce significant operational friction: they require continuous skin contact, cause cutaneous irritation, suffer from motion-induced sensor detachment, and require frequent battery recharging.")
    
    add_body_p(doc, "Remote Photoplethysmography (rPPG) has emerged as a transformative paradigm that eliminates physical contact entirely. By capturing ambient or dedicated light reflections from exposed facial skin using standard RGB video cameras, rPPG extracts subtle, invisible cardiac-synchronous color variations governed by dermal capillary pulsation. When combined with modern deep learning and computer vision architectures, facial rPPG offers the revolutionary capability to perform continuous, passive, and ubiquitous blood pressure monitoring across clinical telehealth kiosks, smart home environments, automotive driver monitoring systems, and mobile smartphones.")

    add_heading_sub1(doc, "1.2 Problem Statement")
    add_body_p(doc, "Despite the profound clinical potential of camera-based rPPG, translating facial video streams into accurate, medical-grade arterial blood pressure measurements constitutes an exceptionally challenging inverse problem characterized by severe physical, optical, and algorithmic bottlenecks:")
    
    add_bullet_p(doc, "Optical Quantization and Low Signal-to-Noise Ratio (SNR): The pulsatile blood volume component (AC signal) accounts for merely 0.1% to 2.0% of total facial reflectance, with the remainder consisting of static tissue and specular reflection (DC component). In consumer 8-bit RGB camera sensors (256 discrete intensity levels per channel), the quantization step size is approximately 0.39%, meaning that subtle physiological micro-pulsations operate directly at or below the sensor noise floor.", bold_prefix="1. ")
    add_bullet_p(doc, "Environmental Illumination Jitter and Motion Artifacts: Ambient lighting fluctuations, indoor fluorescent flicker, and involuntary head micro-movements inject non-stationary noise that heavily overlaps with the cardiac fundamental frequency band (0.7–3.5 Hz). Furthermore, sudden camera Auto-Exposure (AE) adjustments inject catastrophic temporal discontinuities into the waveform.", bold_prefix="2. ")
    add_bullet_p(doc, "The Capillary Windkessel Damping Barrier: Arterial blood pressure waveforms exhibit distinct morphological landmarks—most notably the sharp systolic upstroke, anacrotic notch, and dicrotic notch resulting from aortic valve closure and arterial elasticity. However, as the pulse wave propagates through the arterial tree into facial capillary microvasculature, the high-frequency viscoelastic damping of the vascular wall severely attenuates the dicrotic notch by 1 to 2 orders of magnitude.", bold_prefix="3. ")
    add_bullet_p(doc, "Algorithmic Regression-to-the-Mean ('Template Collapse'): Conventional deep neural networks trained on homogeneous public datasets consistently suffer from regression-to-the-mean. When confronted with noisy or attenuated rPPG inputs, monolithic models learn to minimize mean squared error by predicting population-average normotensive values (~120/80 mmHg), yielding misleadingly low Mean Absolute Error (MAE) while exhibiting near-zero or negative Pearson correlation coefficients (r) across real hypertensive and hypotensive subjects.", bold_prefix="4. ")

    add_heading_sub1(doc, "1.3 Motivation")
    add_body_p(doc, "The overarching motivation of this research is to construct an intelligent, end-to-end computational framework capable of bridging the domain gap between noisy facial video recordings and clinical-grade arterial pressure estimation. By formulating a rigorous, multi-stage pipeline—uniting hardware-level sensor controls, robust facial landmarking, physics-informed chrominance projection, morphology-preserving Savitzky-Golay filtering, and decoupled deep sequential neural networks—we aim to prove that contactless rPPG can achieve clinical compliance under international validation standards (ISO/AAMI SP10).")
    
    add_body_p(doc, "Creating a reliable, non-contact blood pressure estimation engine holds immense societal and healthcare implications. It empowers proactive cardiovascular management for elderly populations, reduces nurse workload in intensive care units (ICUs), provides non-intrusive neonatal and pediatric vital sign tracking, and democratizes preventative health diagnostics across resource-constrained regions via ordinary smartphones.")

    add_heading_sub1(doc, "1.4 Objectives of the Project")
    add_body_p(doc, "To address the defined research problems, this project sets forth the following specific, concrete, and verifiable engineering objectives:")
    
    add_bullet_p(doc, "To implement a hardware-synchronized facial video acquisition pipeline utilizing the Android Camera2 API with locked auto-exposure, fixed white balance, and 30 FPS timestamp logging.", bold_prefix="1. ")
    add_bullet_p(doc, "To construct a real-time facial mesh tracking engine using the 468-point MediaPipe framework, dynamically isolating bilateral malar (cheek) and upper forehead microvascular regions of interest (ROIs).", bold_prefix="2. ")
    add_bullet_p(doc, "To extract robust Blood Volume Pulse (BVP) signals from raw RGB time series using the physics-based Plane-Orthogonal-to-Skin (POS) chrominance projection algorithm.", bold_prefix="3. ")
    add_bullet_p(doc, "To develop a multi-stage signal conditioning engine integrating bandpass filtering (0.7–3.5 Hz) and an adaptive Savitzky-Golay polynomial smoothing filter to preserve high-order waveform derivatives.", bold_prefix="4. ")
    add_bullet_p(doc, "To engineer a comprehensive feature vector capturing temporal, morphological, spectral, and Heart Rate Variability (HRV) parameters from reconstructed pulse waves.", bold_prefix="5. ")
    add_bullet_p(doc, "To design and train a novel deep sequential neural architecture—MODEL-06-SepHead—incorporating a multi-scale 1D-ResNet backbone, Bidirectional Gated Recurrent Units (BiGRU), Multi-Head Self-Attention (MHSA), and decoupled regression heads for independent SBP and DBP estimation.", bold_prefix="6. ")
    add_bullet_p(doc, "To execute a leak-free, 100% subject-independent evaluation on the Multi-Camera Dataset (MCD) comprising 17,943 windows across 599 subjects.", bold_prefix="7. ")
    add_bullet_p(doc, "To evaluate clinical agreement and accuracy against the international ISO/AAMI SP10 standard and British Hypertension Society (BHS) grading criteria.", bold_prefix="8. ")
    add_bullet_p(doc, "To optimize and deploy the end-to-end pipeline onto mobile Android hardware via TensorFlow Lite (TFLite) int8 quantization for real-time edge execution.", bold_prefix="9. ")

    add_heading_sub1(doc, "1.5 Scope of the Project")
    add_body_p(doc, "To maintain scientific rigor and clear architectural boundaries, the scope of this project is precisely delineated in terms of explicit technical inclusions and defined exclusions:")
    
    add_heading_sub2(doc, "1.5.1 In-Scope Technical Inclusions")
    add_bullet_p(doc, "Optical Video Modality: Acquisition and processing of single-camera visible-spectrum (RGB) facial video recordings at standard consumer frame rates (30 FPS) under stable ambient illumination (≥ 150 lux).", bold_prefix="• ")
    add_bullet_p(doc, "Facial Landmarking & Dermal Capillary Tracking: Dynamic tracking of the upper forehead and bilateral malar microvascular regions of interest using 468-point 3D MediaPipe mesh topology.", bold_prefix="• ")
    add_bullet_p(doc, "Physics-Based Signal Conditioning: Plane-Orthogonal-to-Skin (POS) chrominance projection, Butterworth bandpass filtering (0.7–3.5 Hz), and adaptive Savitzky-Golay polynomial smoothing.", bold_prefix="• ")
    add_bullet_p(doc, "Deep Learning Architecture: Development, training, and benchmarking of the MODEL-06-SepHead neural network featuring multi-scale 1D-ResNets, BiGRU sequence modeling, multi-head self-attention, and decoupled SBP/DBP heads.", bold_prefix="• ")
    add_bullet_p(doc, "Clinical Benchmark Evaluation: Offline subject-independent validation on 17,943 10-second windows across 599 participants from the clinical Multi-Camera Dataset (MCD) with 100% clean subject isolation.", bold_prefix="• ")
    add_bullet_p(doc, "Mobile Edge Deployment: Compilation and deployment of an 8-bit quantized TensorFlow Lite (TFLite) inference model onto native Android (Snapdragon 4 Gen 2) smartphone hardware.", bold_prefix="• ")

    add_heading_sub2(doc, "1.5.2 Explicit Exclusions & Out-of-Scope Boundaries")
    add_bullet_p(doc, "Invasive Arterial Catheterization: The project strictly focuses on non-contact optical estimation and does not involve direct invasive arterial line placement or continuous arterial transducer cannulation.", bold_prefix="• ")
    add_bullet_p(doc, "Multi-Lead Clinical ICU Bedside Hardware: The scope does not include hardware integration with intensive care bedside patient monitors, multi-lead clinical ECG telemetry arrays, or hospital central station protocols.", bold_prefix="• ")
    add_bullet_p(doc, "Dual-Sensor Transit-Time Modalities (PTT/PAT): The system is designed as a standalone single-camera solution and explicitly excludes multi-site sensor synchronization requiring contact finger probes, ECG electrodes, or seismocardiography.", bold_prefix="• ")
    add_bullet_p(doc, "Thermal & Multi-Spectral Sensor Hardware: The current implementation operates exclusively on visible RGB image sensors and excludes hardware ingestion from Long-Wave Infrared (LWIR) thermal cameras, short-wave infrared (SWIR), or hyperspectral imaging arrays.", bold_prefix="• ")
    add_bullet_p(doc, "Arrhythmia & Structural Pathology Diagnosis: The algorithmic pipeline is calibrated for hemodynamic blood pressure estimation and does not provide automated diagnostic classification for complex cardiac arrhythmias (e.g., atrial fibrillation, ventricular tachycardia) or structural valvular regurgitation.", bold_prefix="• ")
    add_bullet_p(doc, "Extreme Dynamic Motion & Neonatal Incubator Monitoring: The pipeline requires a relatively stationary subject (seated position with natural micro-movements) and does not cover high-velocity athletic sports telemetry or specialized neonatal incubator monitoring environments.", bold_prefix="• ")

    add_heading_sub1(doc, "1.6 Project Contributions")
    add_body_p(doc, "The primary scientific and technical contributions of this project, embodied in the LuminaBP system, include:")
    
    add_bullet_p(doc, "An End-to-End Contactless Hemodynamic Pipeline: A complete computational pipeline translating raw facial video frames into calibrated arterial pressure estimates.", bold_prefix="• ")
    add_bullet_p(doc, "Savitzky-Golay Morphological Preservation: Demonstration that local least-squares polynomial filtering suppresses 8-bit quantization noise while retaining vital cardiovascular morphology.", bold_prefix="• ")
    add_bullet_p(doc, "Decoupled Architecture Innovation (MODEL-06-SepHead): Development of separate regression heads that eliminate physiological gradient interference between SBP and DBP.", bold_prefix="• ")
    add_bullet_p(doc, "Clinical ISO/AAMI Compliance for DBP: Achievement of a Diastolic BP MAE of 5.91 mmHg across 90 unseen test subjects, satisfying the ISO/AAMI <= 8.0 mmHg standard.", bold_prefix="• ")
    add_bullet_p(doc, "Strict Zero-Leakage Validation: Rigorous 100% subject-level partitioning guaranteeing zero identity overlap across training, validation, and testing folds.", bold_prefix="• ")
    add_bullet_p(doc, "Edge-Native Mobile Deployment: Full deployment of the pipeline onto Android smartphones with sub-50ms inference latency.", bold_prefix="• ")

    add_heading_sub1(doc, "1.7 Organization of the Report")
    add_body_p(doc, "The remainder of this report is structured as follows: Chapter 2 details the vocational training curriculum, foundational computing libraries, machine learning principles, deep learning architectures, and advanced AI frontiers. Chapter 3 provides a comprehensive literature review of optical hemodynamics and cuffless blood pressure estimation. Chapter 4 presents the proposed LuminaBP methodology and system architecture. Chapter 5 details the software, hardware, dataset curation, and mobile implementation. Chapter 6 presents the experimental results, clinical validation, ablation studies, and physiological discussion. Chapter 7 concludes the report and highlights future research directions. Appendix A provides technical specifications of the core engineering pipeline and baseline checkpoints.")
