# Master R&D Roadmap: Advancing Mobile rPPG to Cuffless Blood Pressure Estimation
## Scientific Expansion Blueprint for MODEL-06-SepHead

**Project Status**: Production Architecture — Post MODEL-06-SepHead Baseline Freeze [1]
**Target Model**: MODEL-06-SepHead (Dual-Branch 1D-ResNet + BiGRU + MHSA + Demographic Fusion) [1]
**Baseline Performance**: SBP Window MAE: 11.58 mmHg (Subject MAE: 10.12 mmHg), DBP Window MAE: 6.70 mmHg (Subject MAE: 5.91 mmHg) [1]
**Primary Bottleneck**: severe regression-to-the-mean ("Template Collapse" toward 120/70 mmHg) due to capillary attenuation of the dicrotic notch, 8-bit quantization noise floors, and 30 FPS Nyquist limitations [1]

---

### 1. Executive Summary & Diagnostic Alignment
Your current architecture, **MODEL-06-SepHead**, represents a highly sophisticated sequential deep learning model [1]. However, the severe regression-to-the-mean (Pearson correlation $r \approx 0.35 - 0.39$) reveals a fundamental scientific barrier: **the model is learning demographic priors (population-level expected values) rather than tracking real-time arterial blood pressure variations [1].**

This occurs because:
1. **The Capillary Windkessel Barrier**: Diastolic pressure is primarily encoded in the dicrotic notch (reflecting aortic valve closure and peripheral resistance) [1, 5]. By the time the pulse wave reaches facial microvasculature, the dicrotic notch is attenuated by 1–2 orders of magnitude [1].
2. **Quantization Noise Floor**: The 8-bit RGB camera sensor (256 intensity levels) has a noise floor of ~0.4%, which swallows the tiny 0.1–2.0% pulsatile AC component of the rPPG signal [1].
3. **Sparse Temporal Sampling**: At 30 FPS, the 30–60 ms dicrotic notch spans a mere 1–2 raw samples, which are smeared during interpolation to 125 Hz without generating new morphological details [1].

To break past this "Normotensive Calibration Trap" [3], this roadmap synthesizes cutting-edge frameworks from your uploaded literature—specifically **Topological Signal Processing (MAI)** [2], **Uncertainty-Aware Bayesian Multi-Modal Fusion (U-FaceBP)** [3], **PPG-Guided Feature Alignment (ALIVE)** [4], and **Phase-Shifted Dual-Site rPPG (DRP-Net/BBP-Net)** [5]—to chart an actionable progression path.

---

### 2. Strategic Pivot 1: Conquering Template Collapse with Topological Signal Processing (MAI Framework)
Traditional models attempt to extract geometric waveform morphology (such as systolic upstroke or dicrotic peaks) directly from noisy, attenuated rPPG signals [4]. When light is absorbed by melanin, or when lighting is uneven, the geometric amplitude of the signal is exponentially degraded according to the modified Beer-Lambert law [2]. Conventionally, Z-normalization is applied, but this fails because it scales noise and signal-dependent attenuation linearly, amplifying the noise floor [2].

#### The Solution: Melanin Absorption Invariance (MAI) & Topological Phase-Space Invariance
The **MAI framework** proves that while melanin absorption destroys the *geometric* structure (amplitude/shape) of the optical signal, the underlying *topological* structure (cardiac attractor rhythm and dynamical phase-space regularity) is perfectly preserved [2].

```
Raw rPPG s(t) ──> Z-Normalization ──> Takens Delay Embedding ──> Phase-Space Attractor ──> Topologically Invariant Features
(Geometric Loss)                      x(t) = [s(t), s(t-tau), ..., s(t-(m-1)tau)]             (RQA, Nearest-Neighbor, PCA)
```

1. **Reconstruct the Cardiac Attractor**:
   Using **Takens' Delay Embedding Theorem** [2], reconstruct the multi-dimensional phase-space of the cardiovascular dynamical system from a single, normalized rPPG signal:
   $$\mathbf{x}_i(t) = [s_i(t), s_i(t - 	au), s_i(t - 2	au), \dots, s_i(t - (m-1)	au)]$$
   *   *Where*: $m$ is the embedding dimension ($m \geq 3$ to satisfy $2d_A+1$) [2], and $	au$ is the delay (typically 1–5 samples depending on sampling rate) [2].
2. **Invariance Proof**:
   Since melanin absorption scales the observed signal by a constant factor $lpha = e^{-\mu}$ [2], the Z-normalization step cancels this multiplicative scaling in both the numerator and denominator:
   $$\mathbf{X}_{lpha s} = rac{\mathbf{X}_{\mathrm{raw}, lpha s} - \mu_{lpha s}}{\sigma_{lpha s}} pprox rac{lpha \mathbf{X}_{\mathrm{raw}, s} - lpha \mu_s}{lpha \sigma_s} = \mathbf{X}_s$$ [2]
   This guarantees that any feature extracted from the attractor's topology—which relies strictly on pairwise distances in the embedding matrix $\mathbf{X}$—is mathematically invariant to skin-tone, gain, and contact pressure [2].
3. **Extract Topologically Invariant Features**:
   Implement **Algorithm 1** [2] to extract 5 key topological metrics to feed into your BP regression heads:
   *   **$f_1, f_2$**: Mean nearest-neighbor distances in the embedding space (encoding local attractor density and heart rhythm regularity) [2].
   *   **$f_3$**: Mean log nearest-neighbor distance (representing the local dimensionality of the cardiovascular manifold) [2].
   *   **$f_4$**: First eigenvalue of Principal Component Analysis (PCA) on the attractor, representing principal variance [2].
   *   **$f_5$**: PCA rotation angle, capturing local geometric orientation [2].
   *   **Recurrence Quantitative Analysis (RQA)**: Extract **Recurrence Determinism (RD)**, Laminarity (TT), and Entropy from recurrence plots [2]. These metrics have been empirically shown to achieve a **95% reduction in skin-tone bias** across Fitzpatrick types III–VI under 80 real-world conditions [2].
4. **SNR-Adaptive Correction**:
   To reduce residual bias to $O(\mathrm{SNR}_{\mathrm{eff}}^{-2})$ [2, 3], apply an SNR-adaptive scaling function to the topological features:
   $$\hat{f}_i = g(\mathrm{SNR}) \cdot f_i \quad 	ext{where} \quad g(\mathrm{SNR}) = \left(1 + rac{k}{\mathrm{SNR}}
ight)$$ [2]
   This mathematically counteracts the noise-induced dilation of the attractor under extremely low signal-to-noise ratios (such as under low-light or darker Fitzpatrick types V/VI) [2].

---

### 3. Strategic Pivot 2: Resolving Data Gaps & Noise with Uncertainty-Aware Multi-Modal Fusion (U-FaceBP Paradigm)
A major vulnerability in MODEL-06-SepHead is that it outputs a single deterministic blood pressure prediction [1]. When the input rPPG is highly corrupted by head motion, compression artifacts, or dynamic illumination, the model has no way to express doubt and simply falls back to predicting 120/70 mmHg [1, 3].

#### The Solution: Bayesian Neural Networks (BNN) & Tri-Modal Ensemble
Following the **U-FaceBP framework** [3], convert your deterministic PyTorch model into an uncertainty-aware Bayesian model and implement a tri-modal ensemble.

```
                  ┌───> rPPG BNN (S-Net + Dropout) ───> SBP_rppg, var_rppg ──┐
                  │                                                          │
Facial Video ─────┼───> PPG Reconstruction BNN ───────> SBP_ppg, var_ppg ────┼──> Uncertainty-Driven Aggregator (UDA) ──> Final BP Prediction
                  │                                                          │
                  └───> Pre-trained Face Image BNN ───> SBP_img, var_img ────┘
```

1. **Incorporate Dropout as a Bayesian Approximation**:
   Insert Monte Carlo (MC) dropout layers [3] after each residual block in your Dual-Branch 1D-ResNet and BiGRU [1, 3]. At test time, run $T = 10$ forward passes with dropout enabled to sample from the approximate posterior weight distribution [3].
2. **Output Heteroscedastic Predictive Variance**:
   Modify the final linear layers of your separate SBP and DBP heads [1, 3] to output **two values each**: the predictive mean $\hat{y}$ and the predictive variance $\hat{\sigma}^2$ (representing aleatoric data uncertainty) [3]:
   $$\mathcal{L}_{\mathrm{NLL}}(y) = rac{1}{2} \exp(-s) \|y - \hat{y}\|^2 + rac{1}{2} s \quad 	ext{where} \quad s = \log(\hat{\sigma}^2)$$ [3]
   This loss function prevents overconfident predictions by allowing the network to increase $s$ (attenuating the loss) when the signal is heavily corrupted by noise [3].
3. **Quantify Two Distinct Types of Uncertainty**:
   *   **Aleatoric Uncertainty (Observation Noise)**:
       $$U^{\mathrm{aleatoric}} = rac{1}{T} \sum_{t=1}^{T} \hat{\sigma}_t^2$$ [3]
       This spikes during raw signal degradation (motion blur, low light) [3].
   *   **Epistemic Uncertainty (Model Knowledge Gaps)**:
       $$U^{\mathrm{epistemic}} = rac{1}{T} \sum_{t=1}^{T} \hat{y}_t^2 - \left(rac{1}{T} \sum_{t=1}^{T} \hat{y}_t
ight)^2$$ [3]
       This represents the variance of predictions across MC runs and will spike for patients with severe hypertension or rare clinical profiles, signaling a need for conventional cuff triage [3].
4. **Implement the Tri-Modal Ensemble**:
   Rather than relying solely on the hand-crafted 1D BVP waveform [3]:
   *   **Branch A (rPPG Path)**: Your existing 1D-ResNet processing multi-ROI POS-extracted signals (capturing pulse wave morphology and inter-region PTT) [3].
   *   **Branch B (PPG Path)**: An end-to-end CNN trained to *reconstruct* standard transmission-mode contact PPG signals directly from raw video tensors [3]. This bypasses POS/CHROM to extract raw structural pulse dynamics [3].
   *   **Branch C (Face Image Path)**: A ResNet-50 backbone pre-trained on facial representation learning (FRL) using self-supervised **SwAV** [3]. Fine-tune this branch on static demographic and physiological traits (age, gender, BMI, wrinkles, baldness, facial shape) which strongly correlate with baseline cardiovascular age and blood pressure [3].
5. **Fuse Modalities via the Uncertainty-Driven Aggregator (UDA)**:
   Avoid flat, linear averaging which is highly sensitive to noise. Instead, dynamically weight the predictions of the three branches based on their relative normalized uncertainties [3]:
   $$\hat{y}_{\mathrm{SBP}} = \sum_{m \in \{\mathrm{rppg}, \mathrm{ppg}, \mathrm{img}\}} \mathrm{softmax}\left(-s^{\mathrm{total}}_{m, \mathrm{sbp}}
ight) \cdot \hat{y}^m_{\mathrm{SBP}}$$ [3]
   UDA assigns higher weights to the face image branch in the lower, normal ranges (where baseline appearance features dominate) [3], and automatically shifts weight to rPPG/PPG pulse-wave branches for higher, hypertensive ranges where real-time hemodynamics are essential [3].

---

### 4. Strategic Pivot 3: Improving BVP Morphology with PPG-Guided Feature Alignment (ALIVE Paradigm)
A major bottleneck in your PyTorch training pipeline (`train_bp_mcd.py`) is that the model is trained entirely with Mean Squared Error (MSE) loss directly mapping rPPG to cuff BP [1]. Because rPPG features are highly corrupted by ambient lighting and motion, the loss landscape is chaotic, causing the optimizer to settle on the safe population-mean expected value [1, 3].

#### The Solution: Dual-Branch Cross-Modal Feature Alignment
Following the **ALIVE framework** [4], leverage the fact that contact finger PPG provides pristine cardiovascular waveforms compared to camera rPPG [4]. Use contact PPG during training to "teach" your camera-based encoder how to extract robust, noise-free, BP-relevant features [4].

```
Training Routine (PPG-Guidance):
Face Video clip ──> NrPPG Encoder ──> Fr (rPPG Features) ──┐
                                                           ├──> Feature-Alignment Loss LF (Pearson correlation)
Finger PPG signal ──> NPPG Encoder  ──> Fp (PPG Features)  ──┘
```

1. **Pre-train a PPG-Based BP Model ($N_{\mathrm{PPG}}$)**:
   Pre-train a 1D Temporal Convolutional Network (TCN) [4] or ResNet on large-scale, clinical-grade contact PPG datasets (e.g., MIMIC-III, PPG-BP) to map contact waveforms directly to SBP/DBP [1, 4]. Once trained, **freeze the weights of this network** ($N_{\mathrm{PPG}}$) [4].
2. **Apply Pearson Feature-Alignment Loss ($L_F$)**:
   During PyTorch training of your rPPG model ($N_{\mathrm{rPPG}}$), feed the paired, synchronized contact PPG through the frozen $N_{\mathrm{PPG}}$ to extract high-fidelity feature maps $F_p$ [4]. Extract the corresponding feature maps $F_r$ from your rPPG branch [4]. Force $N_{\mathrm{rPPG}}$ to align its latent space with the pristine PPG features by maximizing their Pearson correlation coefficient:
   $$\mathcal{L}_F = 1 - r(F_r, F_p)$$ [4]
   This acts as a powerful regularizer, forcing the 1D-ResNet/BiGRU layers to ignore lighting noise and specifically isolate key pulse dynamics (systolic upstroke, dicrotic notch, reflection waves) [4, 7].
3. **Transition to Quality-Weighted Temporal Clip Fusion**:
   Instead of analyzing a single, long 7–10 second block that might contain a sneeze, blink, or lighting spike [1, 4]:
   *   Segment the facial video into **4-second non-overlapping clips** [4]. This ensures each clip contains at least two complete cardiovascular cycles, which is the mathematical minimum for BP feature extraction [4].
   *   During inference, estimate SBP and DBP independently for each 4-second clip [4].
   *   Calculate an instantaneous **Signal Quality Index ($q_i$)** for each clip based on its time-frequency spectral power density and cardiac continuity (e.g., using the Wavelet Synchrosqueezed Transform - WSST) [5, 15].
   *   Fuse the individual clip predictions using a **quality-weighted average** [4, 15]:
       $$\hat{P}_{\mathrm{final}} = rac{\sum_{i=1}^{n} q_i \cdot \hat{P}_i}{\sum_{i=1}^{n} q_i}$$ [4]
       This dynamic gating ensures that noisy frames (expressions, motion) are automatically discounted, drastically reducing MAE in real-world deployment [4].

---

### 5. Strategic Pivot 4: Harnessing Pulse Wave Transit Dynamics via Dual Phase-Shifted rPPG (DRP-Net + BBP-Net)
The current MODEL-06-SepHead calculates rPPG from three ROIs (Forehead, Left Cheek, Right Cheek) but merges them into a single averaged 1D signal before feeding it to the deep learning model [1, 5]. This completely discards the **spatial phase difference** (time delay) of blood flow across different facial sites, which is a powerful surrogate marker for Pulse Wave Velocity (PWV) and arterial compliance [4, 5].

#### The Solution: Phase-Shifted Dual-Site Modeling
Adopt the two-stage **DRP-Net + BBP-Net pipeline** [5] to directly model the phase delay between central and peripheral arterial beds.

```
Facial Video ──> DRP-Net (Atrous 3D-CNN + Spatial-Temporal Attention)
                    ├──> Head A: Facial rPPG (Forehead/Cheek bed) ──┐
                    └──> Head B: Acral rPPG (Extremity simulation)  ──┼─> Stack [rPPG, VPG, APG] ─> BBP-Net ─> Scaled Sigmoid ─> BP
```

1. **Extract Facial vs. Acral rPPG**:
   Configure a dual-headed Siamese network (**DRP-Net**) [5] to predict two separate waveforms from the facial video:
   *   **Facial rPPG ($y_f$)**: The blood volume pulse extracted from central facial regions (primarily the cheeks) [5].
   *   **Acral rPPG ($y_a$)**: A reconstructed pulse waveform that mimics the phase of a distal extremity (the index finger PPG) [5].
2. **Derive Velocity and Acceleration Plethysmograms**:
   Do not rely solely on the raw 1D displacement. Compute the first and second mathematical derivatives for both the facial and acral waveforms [3, 5]:
   *   **VPG (Velocity Plethysmogram)**: Represents the blood flow velocity [3, 5].
   *   **APG (Acceleration Plethysmogram)**: Represents blood flow acceleration [3, 5].
   Stack these signals into a **$6 	imes T$ input matrix** [5] consisting of $[y_f, y_a, y'_f, y'_a, y''_f, y''_a]$ to feed into the BP estimation network (**BBP-Net**) [5]. This forces the model to mathematically track the phase delay (Pulse Transit Time) and the acceleration kinetics of the pulse cycle [5].
3. **Incorporate a Physiologically Bounded Scaled Sigmoid**:
   To eliminate wild, unphysiological SBP/DBP predictions that destabilize gradients during training, modify the output layer of your SBP/DBP heads with a **scaling sigmoid function** [5]:
   $$\hat{y}_{\mathrm{BP}} = \mathrm{BP}_{\mathrm{min}} + rac{\mathrm{BP}_{\mathrm{max}} - \mathrm{BP}_{\mathrm{min}}}{1 + \exp(-z + 	au)}$$ [5]
   *   *Where*: $z$ is the raw logit from the BP prediction head, $	au$ is a learned temperature scaling parameter [5], and $\mathrm{BP}_{\mathrm{min}}/\mathrm{BP}_{\mathrm{max}}$ are fixed physiological boundaries:
       *   **SBP Range**: $[80, 180]$ mmHg [5]
       *   **DBP Range**: $[60, 130]$ mmHg [5]
   This bounding mechanism drastically stabilizes training, improves model precision, and forces the network to focus on fine-grained physiological differences rather than absorbing massive outlier errors [5].

---

### 6. Mobile Edge Deployment Optimization (KDPhys & TH-STT Paradigms)
Your target deployment hardware is a **Snapdragon 4 Gen 2 (6GB RAM)** [1, 7], a resource-constrained processor. Running heavy 3D-CNNs, deep BiGRUs, or large ViT models locally in real-time will cause severe thermal throttling, frame rate drops (destroying the Nyquist sampling rate), and rapid battery drain [6, 7].

1. **Spatio-Temporal Knowledge Distillation (KDPhys)**:
   Instead of running a heavy 3D-CNN on-device to capture temporal context, employ **Knowledge Distillation (KD)** [6]. Train a high-capacity 3D-CNN (such as PhysNet) on a GPU server as your **Teacher model** to learn dense spatial-temporal representations [6, 7]. Transfer this rich physiological knowledge into a lightweight, 2D-CNN + Shift-Connection **Student model** (e.g., EfficientPhys) [6]. This achieves a **real-time CPU execution speedup of up to 13%** with negligible accuracy drop [6, 7].
2. **Distilled Spatio-Temporal Transformers (TH-STT)**:
   If exploring attention-based architectures, avoid massive ViT backbones [6]. Utilize a **TH-STT** paradigm [6, 7] with a ViT-Tiny or MobileViT backbone [6]. Apply dynamic background anchors (32x32 pixel upper windows with low spatial gradients) to dynamically estimate and subtract ambient illumination noise [7], while using **Reaction-Driven Gating** to mask out facial muscle movements [7]. This lightweight ~3.9 MB model runs under 0.15s per window on a standard mobile CPU [6, 7].
3. **TFLite Quantization Strategy**:
   Convert PyTorch checkpoints to TensorFlow Lite (`.tflite`) format with **int8 post-training quantization** [6, 7]. This compresses the MODEL-06 model size to $<4$ MB [7], allowing it to run natively on the Snapdragon NPU/GPU using the `Interpreter` API with highly stable execution latency [1, 6, 7].

---

### 7. Upgraded 14-Step Experimental Roadmap
This revised experimental roadmap is designed to replace your current sequence, directly integrating the source-backed paradigms to systematically isolate and resolve the Template Collapse problem.

```
PHASE I: DATA & INTERPOLATION (Steps 1-3)
  └── Phase-Locked Augmentation ──> Multi-ROI Extract ──> Temporal interpolation

PHASE II: TOPOLOGICAL RECONSTRUCTION (Steps 4-6)
  └── Attractor Delay Embedding ──> Feature-Alignment Loss ──> Quality-Weighted Fusion

PHASE III: ADVANCED MODELING & UNCERTAINTY (Steps 7-10)
  └── Tri-Modal Ensemble ──> BNN MC Dropout ──> Scaled Sigmoid Bounds ──> UDA Fusion

PHASE IV: VALIDATION & MOBILIZATION (Steps 11-14)
  └── Subject-Independent BA ──> Cross-Device Domain ──> TFLite int8 Distillation
```

#### Phase I: Data Expansion & Interpolation Rigour
*   **Step 1: Frame Interpolation Augmentation**
    *   *Hypothesis*: The model lacks representation for extreme blood pressure states (hypertension/hypotension) and extreme heart rates, leading to mean-bias [5].
    *   *Implementation*: Run **FILM-Net (Frame Interpolation for Large Motion)** [5, 8] on your video clips to systematically synthesize artificial bradycardia and tachycardia frames, broadening your cardiovascular dynamic distribution [5, 8].
*   **Step 2: Multi-ROI Spatial Patching**
    *   *Hypothesis*: Specular reflection and facial hair unevenly corrupt facial ROIs, destroying the signal [9].
    *   *Implementation*: Segment the face into **5 spatial ROIs** (Forehead, Left Cheek, Right Cheek, Nose, Chin) [9]. Divide each ROI into left and right sub-patches, averaging pixel intensities to maximize spatial robustness and SNR [5, 9].
*   **Step 3: Canonical Correlation & BSS Denoising**
    *   *Hypothesis*: Ambient illumination trends and micro-motions are entangled with the hemoglobin signal [9].
    *   *Implementation*: Apply **Canonical Correlation Analysis (CCA)** [9] across spatial sub-patches to isolate coherent cardiac signals, followed by **Independent Component Analysis (ICA)** [9] and **Ensemble Empirical Mode Decomposition (EEMD)** [9] to strip low-frequency non-stationary lighting drifts.

#### Phase II: Latent Space & Waveform Recovery
*   **Step 4: Topological Attractor Reconstruction**
    *   *Hypothesis*: Melanin-induced amplitude attenuation is destroying the geometric shape of the waveform, causing model failure on dark skin tones [2, 3].
    *   *Implementation*: Implement **Takens' Delay Embedding** [2] on the denoised rPPG signals. Extract topologically invariant features ($f_1$ to $f_5$) and RQA metrics (Recurrence Determinism) [2]. This provides a 95% reduction in skin-tone bias across the entire Fitzpatrick scale [2].
*   **Step 5: PPG-Guided Feature Alignment ($L_F$)**
    *   *Hypothesis*: Directly regressing noisy rPPG signals to cuff BP leads to chaotic loss landscapes and template collapse [4].
    *   *Implementation*: Train a TCN on clinical PPG data ($N_{\mathrm{PPG}}$) and freeze it [4]. Train your rPPG model ($N_{\mathrm{rPPG}}$) with a **Pearson-correlation alignment loss ($L_F$)** [4] to map rPPG feature representations directly to pristine contact PPG representations [4].
*   **Step 6: Quality-Weighted Temporal Fusion**
    *   *Hypothesis*: Temporal noise spikes in long video blocks degrade model performance [4].
    *   *Implementation*: Divide videos into **4-second clips** [4]. Extract SBP/DBP predictions for each clip and fuse them using a **quality-weighted average** based on the spectrogram continuity of the BVP signal, automatically throwing out noisy segments [4, 15].

#### Phase III: Advanced Modeling & Uncertainty
*   **Step 7: Bayesian MC Dropout Integration**
    *   *Hypothesis*: The model is overconfident on noisy, out-of-distribution, or corrupted face scans [3].
    *   *Implementation*: Add dropout layers after each residual block in your Dual-Branch 1D-ResNet [3]. Enable MC Dropout at inference with $T = 10$ runs to compute both aleatoric (data noise) and epistemic (model knowledge) uncertainties [3].
*   **Step 8: Tri-Modal Ensemble Construction**
    *   *Hypothesis*: Using only 1D rPPG signals limits the model's predictive capacity [3].
    *   *Implementation*: Build three parallel BNN branches: **Branch A** (rPPG waveform and PTT features), **Branch B** (deep PPG signal reconstruction), and **Branch C** (FRL pre-trained SwAV ResNet-50 face image branch) [3].
*   **Step 9: Uncertainty-Driven Aggregator (UDA) Fusion**
    *   *Hypothesis*: Fixed linear weighting of ensemble modalities is sub-optimal [3].
    *   *Implementation*: Apply the **UDA framework** [3] to dynamically weight the three branches based on their relative, scale-normalized uncertainties, heavily weighting static facial traits in normal ranges and hemodynamics in hypertensive ranges [3].
*   **Step 10: Scaled Sigmoid Boundary Constraints**
    *   *Hypothesis*: Unbounded regression outputs cause massive gradient instability and poor convergence [5].
    *   *Implementation*: Incorporate a **scaled sigmoid function** [5] on SBP and DBP heads to strictly constrain predicted blood pressure within a physiological range of $80 - 180$ mmHg (SBP) and $60 - 130$ mmHg (DBP) [5].

#### Phase IV: Strict Validation & Edge Mobilization
*   **Step 11: Class-Imbalance Label Distribution Smoothing (LDS)**
    *   *Hypothesis*: The skewness of blood pressure data toward the normotensive center (~120/80 mmHg) causes regression-to-the-mean [3, 5].
    *   *Implementation*: Exclude extreme outliers ($SBP \geq 180$ or $DBP \geq 130$) [5] and implement **Label Distribution Smoothing (LDS)** [5] using a triangular kernel and inverse-frequency reweighting to artificially boost loss gradients for underrepresented hypertensive/hypotensive ranges [5].
*   **Step 12: Subject-Independent Bland-Altman Validation**
    *   *Hypothesis*: Temporal overlap, random splits, or demographic leakage lead to heavily inflated, false accuracy metrics [7].
    *   *Implementation*: Enforce a strict **Subject-Independent K-Fold Cross-Validation (K=5)** [3] split where no subject's windows are shared between training, validation, and testing sets [3, 5]. Evaluate performance using **Bland-Altman agreement plots** [1, 11], verifying if $\geq 85\%$ of predictions fall within the clinically accepted $\pm 10$ mmHg threshold [10].
*   **Step 13: Cross-Device & Demographic Domain Adaptation**
    *   *Hypothesis*: The model trained on a specific camera sensor or cohort (e.g., MCD-Iriun) fails when deployed on other smartphones [7, 13].
    *   *Implementation*: Pre-train your models on large-scale public datasets representing diverse conditions (e.g., **CLBP-300** with 300 subjects in indoor/outdoor lux [12], **MCD-rPPG** with 600 subjects recorded at 3 angles [7, 13], and **iBVP** with synchronized RGB and thermal frames [14]), then perform domain adaptation or fine-tuning [3, 7, 15].
*   **Step 14: Mobile Edge Knowledge Distillation & TFLite Deployment**
    *   *Hypothesis*: The final model is too computationally heavy for Snapchat 4 Gen 2 hardware [1, 7].
    *   *Implementation*: Distill spatiotemporal features from your heavy PyTorch model into a lightweight Student network [6]. Export to TFLite format using **int8 post-training quantization** [6, 7] and utilize GPU/NPU acceleration via the Android `Interpreter` API [1, 7].

---

### References & Bibliography

[1] **Upadhyay, V. (2026).** "Mobile rPPG to Cuffless Blood Pressure Estimation: Technical Reference and Baseline Architecture (MODEL-06-SepHead)." *MASTER_PROJECT_CONTEXT.md*, Version 1.0, August 2026.

[2] **Oladunni, T., & Adewumi, F. G. (2026).** "Skin-Tone-Invariant Topological Signal Processing: A Framework for Bias-Reducing Optical Measurement Systems." *medRxiv preprint*, doi: 10.64898/2026.08.01.26359472.

[3] **"U-FaceBP: Uncertainty-aware Bayesian Ensemble Deep Learning for Face Video-based Blood Pressure Measurement."** *arXiv preprint*, arXiv:2412.10679.

[4] **Saikia, T., et al. (2026).** "BP-rPPG: An Indian Face-Video Dataset and PPG-Guided Baseline for Remote Blood Pressure Estimation." *ALIVE Framework Technical Report*.

[5] **Hwang, G., et al. (2024).** "Phase-shifted Remote Photoplethysmography for Estimating Heart Rate and Blood Pressure from Facial Video." *arXiv preprint*, arXiv:2401.04560.

[6] **Sahoo, N. N., Sachidanand, V. S., Gayathri, M. N., Murugesan, B., Ram, K., Joseph, J., & Sivaprakasam, M. (2026).** "KDPhys: An Attention Guided 3D to 2D Knowledge Distillation for Real-time Video-Based Physiological Measurement." *Biomedical Signal Processing and Control*, arXiv:2601.00714.

[7] **Mehrez, A., Alsammak, A., & El-Mashad, S. Y. (2026).** "Remote Photoplethysmography Using Triple-Head Spatio-Temporal Transformer with Reaction-Driven Gating and Illumination Separation." *Sensors*, 26(11), 3490. doi: 10.3390/s26113490.

[8] **Reda, F., et al. (2022).** "FILM: Frame Interpolation for Large Motion." *European Conference on Computer Vision (ECCV)*.

[9] **"Computational Pipelines, Deep Learning Architectures, and Clinical Validation Standards in Smartphone-Based Remote Photoplethysmography for Blood Pressure Estimation."** *Biomedical Engineering & Signal Processing Synthesis Reference*.

[10] **Graßl, T., et al. (2026).** "A Universal Standard for the Validation of Blood Pressure Measuring Devices." *Hypertension - American Heart Association Journals*.

[11] **Bland, J. M., & Altman, D. G. (1986).** "Statistical methods for assessing agreement between two methods of clinical measurement." *The Lancet*, 327(8476), 307-310.

[12] **Al-Naji, A., Jabar, M., Mahmood, M. F., Al-Nakkash, A., Alsabah, M. S., Khalid, G. A., & Chahl, J. (2026).** "CLBP-300: A Real-World Video Dataset for Cuff-Less Blood Pressure Estimation via rPPG." *MDPI / Preprints*.

[13] **Savchenko, A., et al. (2025).** "Gaze into the Heart: A Multi-View Video Dataset for rPPG and Health Biomarkers Estimation." *ACM Multimedia*.

[14] **Joshi, Y. C., & Cho, J. (2024).** "iBVP Dataset: RGB-Thermal rPPG Dataset With High Resolution Signal Quality Labels." *Preprints.org*.

[15] **Chen, S., et al. (2025).** "An image enhancement based method for improving rPPG extraction under low-light illumination." *Biomedical Signal Processing and Control*, 100, 106963.
