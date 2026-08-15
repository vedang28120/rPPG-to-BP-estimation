# ☁️ Rigorous PPG → BP Model Training (Google Colab GPU)

This package implements every requirement specified in **`PPG_to_BP_Model_Training_Instructions.md`**.

---

## 🔬 Key Specifications Implemented

1. **Strict Subject-Level Split (70/15/15)**:
   - Partitioning is performed strictly by `subject_id` (`GroupShuffleSplit`).
   - All windows, recordings, and physiological states for a given subject remain in a single partition (no subject or temporal leakage).

2. **10-Second Windowing & Quality Gating**:
   - Window length = **10 seconds** (1250 samples at 125 Hz), **50% overlap** (5s step).
   - Rejects flatlines, NaNs, and abnormal amplitudes, logging rejection metrics.
   - Per-window Z-score normalization `(x - mean) / std`.

3. **Derivatives (3 Channels)**:
   - Channels: `[PPG, vPPG (1st derivative), aPPG (2nd derivative)]`.

4. **Dual-Branch Architecture**:
   - **Branch A (Morphology)**: Conv1D + Residual Blocks with kernel size $k=5$.
   - **Branch B (Temporal Receptive Field)**: Conv1D + Residual Blocks with dilated kernel size $k=11$, dilation=2.
   - **BiGRU**: 2-layer Bidirectional GRU (hidden size 64).
   - **Multi-Head Self-Attention**: 4-head attention.
   - **Demographic Fusion**: MLP encoding normalized `[Age, Gender, BMI]`.

5. **Ablation Ladder & Baselines**:
   - Includes **Baseline 1 (Population Mean)** and logs both **Window-level MAE/RMSE** and **Subject-level MAE/RMSE**.

---

## 🚀 How to Run on Google Colab

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload **`colab_training/train_bp_mcd_colab.ipynb`**.
3. Enable Accelerator: **Runtime** $\rightarrow$ **Change runtime type** $\rightarrow$ **T4 GPU** $\rightarrow$ **Save**.
4. Run all cells and enter your **Hugging Face User Access Token** when prompted in Cell 2.
