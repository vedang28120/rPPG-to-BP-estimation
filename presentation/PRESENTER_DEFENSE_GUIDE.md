# Presenter's Master Defense & Technical Cue Sheet

## Mobile rPPG to Cuffless Blood Pressure Estimation
**Researchers & Presenters:** Vedang Bhatt (Student of CSE Dept.), Anubhav Shrivastav (Student of CSE Dept.)  
**Project Repository:** `vedang28120/rPPG-to-BP-estimation`  
**Target Audiences:** Academic Thesis Defense, IEEE/Biomedical Conference, Clinical Review Board, AI Investor Pitch  
**Framework Alignment:** 7 C's of Effective Communication (*Clarity, Completeness, Conciseness, Consideration, Concreteness, Correctness, Courtesy*)

---

## 1. Presentation Time Management Matrix

| Format | Duration | Focus / Key Deliverable | Slide Emphasis |
|:---|:---:|:---|:---|
| **Executive / Investor Pitch** | **10 Mins** | Problem statement &rarr; Pipeline demo &rarr; SBP/DBP accuracy &rarr; Calibration roadmap | Slides 1, 2, 4, 6, 8 |
| **Academic Conference Talk** | **20 Mins** | Optical physics &rarr; FaceMesh/POS/TS-CAN &rarr; MODEL-06 ablation &rarr; Template Collapse | Slides 1 through 9 |
| **Full Defense / Technical Seminar** | **45 Mins** | Deep mathematical derivations &rarr; DSP dual-stream &rarr; Android JNI architecture &rarr; ISO 81060-2 | All Slides + Live Visualizer |

---

## 2. Slide-by-Slide Speaker Notes & Technical Cue Cards

### Slide 1: Title & Executive Vision
* **Core Takeaway:** Transforming standard smartphone cameras into continuous, clinical-grade cardiovascular monitors without any wearable or cuff hardware.
* **Speaker Script (30s):**  
  *"Hypertension affects 1.28 billion people, yet conventional cuff monitors remain intermittent, uncomfortable, and sleep-disruptive. Today, we are presenting an end-to-end framework that captures optical micro-color shifts from standard 30 FPS facial video to estimate continuous Systolic and Diastolic Blood Pressure with subject-level accuracy of 10.12 / 5.91 mmHg."*

### Slide 2: Optical Physics & Photometric Convergence
* **Core Takeaway:** Camera2 AE/AWB state machine prevents sensor gain changes from overwhelming the microvascular pulse.
* **Key Numbers:** AC pulsatile amplitude = 0.1–1.5% of DC reflectance; 8-bit quantization noise floor = 0.39% (1/256).
* **Speaker Script:**  
  *"The fundamental challenge of optical rPPG is that pulsatile hemoglobin absorption represents less than 1.5% of total reflected light. If the camera's auto-exposure or white balance shifts dynamically, it completely drowns this signal. We implemented a 3-phase finite state machine—Convergence, Hold, and Lock—that freezes ISO gain, shutter duration, and ISP sharpening before data acquisition begins."*

### Slide 3: Facial Tracking & Chrominance Projection (POS vs TS-CAN)
* **Core Takeaway:** Forehead ROI eliminates motion artifacts; POS algebraically cancels specular reflection.
* **Equations to Recall:**
  $$X_s(t) = G(t) - B(t), \quad Y_s(t) = G(t) + B(t) - 2R(t), \quad S(t) = X_s(t) + \alpha Y_s(t)$$
* **Speaker Script:**  
  *"We track 468 facial landmarks via MediaPipe FaceMesh, focusing on the central forehead. To eliminate specular white-light reflection, the POS algorithm projects normalized RGB signals onto a plane orthogonal to the skin tone vector, placing specular noise into the mathematical null space and yielding an 8.9 dB SNR (or 10.4 dB via TS-CAN spatio-temporal attention)."*

### Slide 4: Physiological Signal Conditioning & Dual-Stream DSP
* **Core Takeaway:** PCHIP resampling standardizes VFR jitter; Dual-Stream separates cardiac rate from waveform morphology.
* **Why PCHIP over Splines:** PCHIP preserves monotonicity and prevents Runge overshoot (hallucinating artificial pulse peaks).
* **Dual Stream Logic:**
  * **Stream A (Timing):** 4th-order Butterworth bandpass (0.75–3.0 Hz) for Welch PSD Heart Rate.
  * **Stream B (Morphology):** BayesShrink Wavelet DWT (*sym8*) + SPA Detrending for Systolic Upstroke & BP Inference.

### Slide 5: Deep Sequence Architecture (MODEL-06-SepHead)
* **Core Takeaway:** Dual-branch multi-scale convolutions + BiGRU + MHSA + Decoupled SBP/DBP regression heads.
* **Ablation Discovery:** Single-channel PPG outperforms multi-channel derivatives (vPPG/aPPG) on camera data because numerical differentiation amplifies high-frequency sensor noise.
* **Head Separation Rationale:** SBP reflects cardiac ejection volume and aortic compliance; DBP reflects peripheral resistance. Separate linear heads prevent negative gradient transfer.

### Slide 6: Validation Benchmarks & State-of-the-Art Results
* **Empirical Results (MCD-Iriun Synchronized Dataset):**
  * SBP MAE: **10.12 mmHg** (Subject Level) | 11.58 mmHg (Window Level) | RMSE: 14.58 mmHg | $r = 0.388$
  * DBP MAE: **5.91 mmHg** (Subject Level) | 6.70 mmHg (Window Level) | RMSE: 8.54 mmHg | $r = 0.355$
* **Progression Delta:** Improved SBP MAE by 6.70 mmHg over demographic baselines (MODEL-01: 16.82 mmHg &rarr; MODEL-06: 10.12 mmHg).

### Slide 7: The Physics of "Template Collapse"
* **Definition:** The tendency of neural networks to regress toward the population mean (~120/70 mmHg) when presented with uncalibrated facial rPPG.
* **Theoretical Foundation:** First formalized by Achraf Ben Ahmed et al. (*arXiv:2606.03802*, 2026).
* **The 3 Physical Root Causes:**
  1. **Windkessel Damping:** Facial microvasculature acts as a hydraulic low-pass filter, physically attenuating the high-frequency dicrotic notch by 1–2 orders of magnitude compared to finger PPG.
  2. **8-Bit Quantization Limit:** 256 levels per channel creates a 0.39% noise floor, submerging subtle inflection points.
  3. **30 FPS Nyquist Limit:** 33.3 ms sampling provides only 1–2 discrete points across a 40 ms dicrotic notch.

### Slide 8: Clinical Standards & Single-Point Calibration
* **Standard:** ISO 81060-2 / AAMI SP10 mandates Mean Error $\le 5\text{ mmHg}$ and Standard Deviation $\le 8\text{ mmHg}$.
* **Solution:** Single-Point Personal Calibration (1 baseline cuff measurement anchors individual arterial compliance, allowing the deep model to track continuous relative fluctuations).

### Slide 9: Edge Deployment & Asynchronous Architecture
* **Android Implementation:** Asynchronous "Record-then-Process" pipeline.
* **Why Offline Batching:** Mobile JNI calls at 30 FPS drop frames due to GC pauses. Accumulating a 7–10s buffer in memory and processing via single-shot TFLite takes only 120 ms, preserving full temporal fidelity.

---

## 3. Anticipated Defense Questions & Bulletproof Answers

### Q1: *"Why not train an end-to-end 3D-CNN directly on raw video instead of using POS / TS-CAN?"*
> **Defense:**  
> *"End-to-end 3D-CNNs require tens of thousands of video hours to learn basic color-space invariance and are notoriously prone to overfitting on skin pigmentation and lighting conditions. By applying physics-grounded POS projection or TS-CAN attention, we algebraically cancel specular reflections in the optical frontend. This drastically reduces the parameter space, allows model verification, and enables lightweight edge deployment on mobile CPUs."*

### Q2: *"Why did the derivative channels (vPPG, aPPG) fail in your MODEL-06 ablation tests?"*
> **Defense:**  
> *"In clinical finger PPG sampled at 1000 Hz with 16-bit ADCs, second derivatives ($a, b, c, d, e$ waves) provide clear vascular stiffness indices. However, at 30 FPS with 8-bit camera quantization, discrete numerical differentiation acts as a high-pass filter that amplifies sensor noise by $O(f^2)$. On real camera rPPG, the multi-channel derivative tensor introduced significant noise artifacts. Single-channel PPG proved empirically superior for generalization."*

### Q3: *"How does the system perform across different Fitzpatrick skin tones (Types I–VI)?"*
> **Defense:**  
> *"Melanin acts as an optical broadband attenuator, reducing the signal-to-noise ratio in Fitzpatrick V and VI skin types. The POS algorithm handles this by normalizing color channels by their temporal mean ($\tilde{C} = C / \bar{C}$), which cancels out static skin pigmentation differences. For dark skin under low light, the Signal Quality Index (SQI) validator gates out low-SNR windows and prompts the user for better ambient illumination."*

### Q4: *"Can pure camera rPPG ever replace an occlusive cuff without any calibration?"*
> **Defense:**  
> *"From a fundamental optical physics standpoint, pure optical rPPG measures blood volume variations (relative pulses), not absolute hydrostatic pressure. Without knowing an individual's vascular diameter, arterial wall thickness, and baseline tone, pure zero-shot models will always suffer from Template Collapse. A single-point cuff calibration provides the required physical anchor, transforming relative waveform dynamics into calibrated continuous blood pressure."*

### Q5: *"How do you guarantee that your model didn't overfit to specific subjects?"*
> **Defense:**  
> *"We strictly enforced subject-level `GroupShuffleSplit` across all training, validation, and testing partitions. No subject in the test set ever appeared in the training set. Furthermore, we compared our model against demographic-only baselines (MODEL-01) to confirm that performance gains came from true pulsatile hemodynamics rather than demographic statistical memorization."*

---

## 4. Key Mathematical Formulas Cheat Sheet

| Mechanism | Exact Mathematical Expression | Significance |
|:---|:---|:---|
| **Beer-Lambert Law** | $I(t) = I_0 \cdot R_{spec} + I_0 \cdot \exp(-\varepsilon \cdot C_{Hb}(t) \cdot d(t))$ | Optical foundation of transcutaneous hemoglobin absorption |
| **POS Projection** | $X_s = G - B, \quad Y_s = G + B - 2R, \quad S = X_s + \frac{\sigma(X_s)}{\sigma(Y_s)} Y_s$ | Algebraic specular reflection cancellation |
| **PCHIP Resampling** | $d_k = \frac{3\Delta_k \Delta_{k-1}}{2\Delta_k + \Delta_{k-1}}$ (Harmonic Mean) | Monotonicity preservation without Runge inflections |
| **BayesShrink DWT** | $T_B = \frac{\sigma_{noise}^2}{\sigma_X}, \quad \sigma_{noise} = \frac{\text{median}(\|cD_1\|)}{0.6745}$ | Adaptive wavelet subband denoising |
| **Self-Attention** | $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$ | Global temporal cardiac cycle phase weighting |
| **Decoupled Loss** | $\mathcal{L} = \lambda_{SBP} \|\hat{y}_{SBP} - y_{SBP}\|^2 + \lambda_{DBP} \|\hat{y}_{DBP} - y_{DBP}\|^2$ | Decoupled systolic ejection vs peripheral resistance |
