"""
PPG-Guided Cross-Modal Feature Alignment (ALIVE Paradigm)
Reference: ALIVE Framework (IEEE TBME / CVPR).
Implements:
  1. Pre-trained Contact PPG Encoder (N_PPG).
  2. Camera rPPG Encoder (N_rPPG).
  3. Latent Space Pearson Feature-Alignment Loss: L_F = 1 - r(F_r, F_p).
Forces the camera-based model to extract pristine pulse morphology (systolic upstroke, dicrotic notch)
by aligning its latent space with contact PPG features.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class PPGEncoderTCN(nn.Module):
    """
    1D Temporal Convolutional Network (TCN) encoding high-fidelity contact PPG waveforms.
    """
    def __init__(self, in_channels=1, feat_dim=128):
        super(PPGEncoderTCN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv1d(in_channels, 32, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, feat_dim, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(feat_dim),
            nn.ReLU()
        )
        self.fc = nn.Linear(feat_dim, 2)  # [SBP, DBP]

    def forward(self, wave):
        feat_map = self.conv1(wave)        # (B, 128, L_down)
        pooled = torch.mean(feat_map, dim=-1) # (B, 128)
        out = self.fc(pooled)
        return out, feat_map, pooled

def pearson_correlation_loss(f_r, f_p):
    """
    Computes Pearson Correlation Loss between rPPG features (f_r) and PPG features (f_p):
    L_F = 1 - r(f_r, f_p)
    """
    # Flatten spatial/channel dimensions: (B, D)
    f_r_flat = f_r.view(f_r.size(0), -1)
    f_p_flat = f_p.view(f_p.size(0), -1)

    # Zero-center
    f_r_cent = f_r_flat - torch.mean(f_r_flat, dim=1, keepdim=True)
    f_p_cent = f_p_flat - torch.mean(f_p_cent, dim=1, keepdim=True)

    # Covariance and variances
    cov = torch.sum(f_r_cent * f_p_cent, dim=1)
    var_r = torch.sum(f_r_cent ** 2, dim=1)
    var_p = torch.sum(f_p_cent ** 2, dim=1)

    eps = 1e-8
    r = cov / (torch.sqrt(var_r * var_p) + eps)
    
    # Loss: 1 - mean(r)
    return torch.mean(1.0 - r)

class ALIVEAlignmentModel(nn.Module):
    """
    ALIVE framework combining rPPG and contact PPG encoders with cross-modal alignment loss.
    """
    def __init__(self, rppg_encoder, ppg_encoder=None, lambda_align=0.5):
        super(ALIVEAlignmentModel, self).__init__()
        self.rppg_encoder = rppg_encoder
        self.ppg_encoder = ppg_encoder if ppg_encoder is not None else PPGEncoderTCN(in_channels=1)
        self.lambda_align = lambda_align

    def freeze_ppg_encoder(self):
        for param in self.ppg_encoder.parameters():
            param.requires_grad = False
        self.ppg_encoder.eval()

    def forward(self, rppg_wave, ppg_wave=None, demo=None):
        rppg_preds = self.rppg_encoder(rppg_wave, demo) if demo is not None else self.rppg_encoder(rppg_wave)
        
        if ppg_wave is not None and self.training:
            with torch.no_grad():
                ppg_preds, ppg_feat_map, ppg_pooled = self.ppg_encoder(ppg_wave)
            return rppg_preds, ppg_pooled
            
        return rppg_preds
