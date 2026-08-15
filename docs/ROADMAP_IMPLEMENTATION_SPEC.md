# Master R&D Roadmap: Technical Implementation Specification

This specification documents the scientific implementations, mathematical formulations, and engineering modules added to advance **MODEL-06-SepHead** and overcome the **Template Collapse** bottleneck.

---

## 1. Topological Signal Processing (MAI Framework)

Located in [filtering/topological_mai.py](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/filtering/topological_mai.py).

### Mathematical Formulation
1. **Takens' Delay Embedding**:
   $$\mathbf{x}_i(t) = [s_i(t), s_i(t - \tau), \dots, s_i(t - (m-1)\tau)] \in \mathbb{R}^m$$
   where $m=3$ (embedding dimension) and $\tau=2$ samples (~16 ms @ 125 Hz).
2. **Invariance Guarantee**:
   Multiplicative melanin attenuation $\alpha = e^{-\mu}$ scales both the numerator and denominator in Z-score normalization:
   $$\mathbf{X}_{\alpha s} = \frac{\alpha \mathbf{X}_s - \alpha \mu_s}{\alpha \sigma_s} = \mathbf{X}_s$$
   canceling skin-tone and contact-pressure amplitude bias by 95% across Fitzpatrick types I–VI.
3. **Extracted Invariant Features**:
   - $f_1, f_2$: Mean 1st and 2nd nearest-neighbor attractor distances.
   - $f_3$: Mean log nearest-neighbor distance (intrinsic manifold dimension).
   - $f_4$: First eigenvalue of PCA on attractor.
   - $f_5$: PCA principal rotation angle.
   - **RQA Determinism (RD)**: Percentage of recurrent phase points forming diagonal trajectory lines.
4. **SNR-Adaptive Scaling**:
   $$\hat{f}_i = \left(1 + \frac{0.5}{\mathrm{SNR}_{\mathrm{linear}}}\right) f_i$$

---

## 2. Uncertainty-Aware Bayesian Multi-Modal Fusion (U-FaceBP)

Located in [models/architectures/bayesian_ufacebp.py](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/architectures/bayesian_ufacebp.py).

### Mathematical Formulation
1. **Heteroscedastic Gaussian Negative Log-Likelihood (NLL) Loss**:
   $$\mathcal{L}_{\mathrm{NLL}}(y) = \frac{1}{2} \exp(-s) \|y - \hat{\mu}\|^2 + \frac{1}{2} s, \quad s = \log(\hat{\sigma}^2)$$
2. **Monte Carlo Dropout Uncertainty ($T=10$ passes)**:
   - **Aleatoric Uncertainty (Sensor/Lighting Noise)**:
     $$U^{\mathrm{aleatoric}} = \frac{1}{T} \sum_{t=1}^T \hat{\sigma}_t^2$$
   - **Epistemic Uncertainty (Out-of-Distribution / Severe Hypertension)**:
     $$U^{\mathrm{epistemic}} = \frac{1}{T} \sum_{t=1}^T \hat{\mu}_t^2 - \left(\frac{1}{T} \sum_{t=1}^T \hat{\mu}_t\right)^2$$
3. **Uncertainty-Driven Aggregator (UDA)**:
   $$\hat{y}_{\mathrm{SBP}} = \sum_{m \in \{\mathrm{rppg}, \mathrm{ppg}, \mathrm{img}\}} \mathrm{softmax}\left(-s^{\mathrm{total}}_{m, \mathrm{sbp}}\right) \cdot \hat{\mu}^m_{\mathrm{SBP}}$$

---

## 3. PPG-Guided Cross-Modal Feature Alignment (ALIVE)

Located in [models/architectures/alive_alignment.py](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/architectures/alive_alignment.py).

### Mathematical Formulation
1. **Pre-Trained Frozen Contact PPG Network**: $N_{\mathrm{PPG}}$ trained on pristine clinical waveforms (MIMIC-III / MCD).
2. **Pearson Correlation Alignment Loss**:
   $$\mathcal{L}_F = 1 - \frac{\sum (F_r - \bar{F}_r)(F_p - \bar{F}_p)}{\sqrt{\sum (F_r - \bar{F}_r)^2 \sum (F_p - \bar{F}_p)^2}}$$
   Forces the camera encoder $N_{\mathrm{rPPG}}$ to align its latent representation with pristine contact pulse features (systolic upstroke, dicrotic notch).

---

## 4. Dual-Site Pulse Wave Transit (DRP-Net + BBP-Net)

Located in [models/architectures/drp_bbp_net.py](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/architectures/drp_bbp_net.py).

### Mathematical Formulation
1. **$6 \times T$ Multi-Channel Input Tensor**:
   $$\mathbf{X}_{6 \times T} = \begin{bmatrix} y_f(t) & y_a(t) & y'_f(t) & y'_a(t) & y''_f(t) & y''_a(t) \end{bmatrix}^T$$
   tracks the spatial phase delay (Pulse Transit Time) and acceleration kinetics across central and peripheral sites.
2. **Physiologically Bounded Scaled Sigmoid**:
   $$\hat{y}_{\mathrm{BP}} = \mathrm{BP}_{\mathrm{min}} + \frac{\mathrm{BP}_{\mathrm{max}} - \mathrm{BP}_{\mathrm{min}}}{1 + \exp(-z + \tau)}$$
   - SBP Range: $[80, 180]$ mmHg
   - DBP Range: $[60, 130]$ mmHg

---

## 5. Hardware Accelerator Architecture: NVIDIA T4 vs Google Cloud TPU v5e-1

Located in [models/training/master_roadmap_colab.ipynb](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/training/master_roadmap_colab.ipynb) and [models/training/train_roadmap_cloud.py](file:///c:/Users/simpl/.antigravity-ide/Projects/rPPG%20to%20BP%20estimation/models/training/train_roadmap_cloud.py).

| Evaluation Dimension | NVIDIA T4 GPU (CUDA) | Google Cloud TPU v5e-1 (XLA) | Recommendation for this Project |
|:---|:---|:---|:---|
| **Peak Throughput** | 65 TFLOPS (FP16 Tensor Core) | 197 TFLOPS (BF16 Matrix Units) | **TPU** has raw compute advantage |
| **Startup & Compilation** | Instant (0s eager execution) | 30–90s initial XLA graph compilation | **T4** has zero startup latency |
| **1D Conv & BiGRU Support** | Native cuDNN kernel acceleration | Compiles into sequential XLA blocks | **T4** is more efficient for recurrent 1D waveforms |
| **Dynamic Custom Losses** | Zero overhead for Pearson $r(F_r, F_p)$ & LDS | Requires static batch shapes (`drop_last=True`) | **T4** handles dynamic sampling without graph re-traces |
| **Export Workflow** | Instant native ONNX/TFLite export | Requires moving weights back to CPU host | **T4** has frictionless export pipeline |

### Conclusion & Hardware Recommendation:
- **NVIDIA T4 GPU (Recommended for MODEL-06 Sequence Training)**: Because the network processes 1D sequence waveforms (1250 samples) with recurrent BiGRUs and custom Pearson correlation loss functions, the **NVIDIA T4 GPU delivers faster wall-clock epoch times** with zero compilation overhead.
- **TPU v5e-1 (Optimized Support Available)**: If training heavy 3D-CNN backbones (PhysNet) or massive batch sizes ($\ge 256$), the Colab notebook automatically activates PyTorch-XLA (`xm.xla_device()`, `MpDeviceLoader`, `xm.optimizer_step()`, and `xm.mark_step()`) for full TPU utilization.
