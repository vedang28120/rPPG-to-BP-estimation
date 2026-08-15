# Model Architectures Submodule (`models/architectures/`)

## Purpose
Defines deep neural network graphs, residual blocks, Bayesian uncertainty heads, cross-modal alignment layers, and physiologically bounded regression heads.

## Dependencies
- External Libraries: `torch`, `torch.nn`, `tensorflow`, `tf_keras`
- Internal Modules: Instantiated by `models/training/` and `models/inference/`

## Key Files
- `bayesian_ufacebp.py`: Implements Bayesian ResNet-BiGRU with Monte Carlo (MC) Dropout, heteroscedastic predictive mean + log-variance regression heads, and the Uncertainty-Driven Aggregator (UDA).
- `alive_alignment.py`: Implements the ALIVE cross-modal feature alignment framework pairing a pre-trained frozen contact PPG encoder ($N_{\mathrm{PPG}}$) with a camera rPPG encoder ($N_{\mathrm{rPPG}}$) via Pearson correlation loss ($\mathcal{L}_F$).
- `drp_bbp_net.py`: Implements the $6 \times T$ multi-site pulse transit network (DRP-Net + BBP-Net) and Scaled Sigmoid physiological bounding ($[80, 180]$ SBP, $[60, 130]$ DBP).
- `resnet_bigru_attn.py`: The baseline MODEL-06 architecture consisting of dual-branch 1D residual convolutions, bidirectional GRU, multi-head self-attention (MHSA), and demographic feature fusion with optional MC Dropout.
- `demo_mlp.py`: Baseline multi-layer perceptron (MODEL-01) mapping static demographic priors directly to mean arterial pressure parameters.
- `legacy_lstm.py`: The legacy MIMIC-III pre-trained recurrent neural network architecture accepting 7-second single-channel normalized PPG windows.
