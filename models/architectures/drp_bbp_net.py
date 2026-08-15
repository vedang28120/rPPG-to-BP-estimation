"""
Dual Phase-Shifted rPPG & Pulse Transit Architecture (DRP-Net + BBP-Net)
Reference: DRP-Net / BBP-Net (IEEE TBME / EMBC).
Implements:
  1. 6xT Multi-Channel Input Tensor: [y_f, y_a, y'_f, y'_a, y''_f, y''_a]
     (Facial & Acral rPPG, Velocity Plethysmogram VPG, Acceleration Plethysmogram APG).
  2. BBP-Net 1D Dilated Residual Network with Transit Time (PTT) Cross-Attention.
  3. Physiologically Bounded Scaled Sigmoid Activation (SBP: [80, 180], DBP: [60, 130] mmHg).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ScaledSigmoidBP(nn.Module):
    """
    Constrains raw network logits z to exact physiological blood pressure boundaries:
    y_hat = BP_min + (BP_max - BP_min) / (1 + exp(-z + tau))
    """
    def __init__(self, sbp_min=80.0, sbp_max=180.0, dbp_min=60.0, dbp_max=130.0):
        super(ScaledSigmoidBP, self).__init__()
        self.sbp_min = sbp_min
        self.sbp_max = sbp_max
        self.dbp_min = dbp_min
        self.dbp_max = dbp_max
        # Learnable temperature scaling parameter tau
        self.tau = nn.Parameter(torch.zeros(1, 2))

    def forward(self, z):
        """
        z: Tensor of shape (B, 2) representing unconstrained logits for [SBP, DBP].
        """
        sig = torch.sigmoid(z - self.tau)
        
        sbp_pred = self.sbp_min + (self.sbp_max - self.sbp_min) * sig[:, 0:1]
        dbp_pred = self.dbp_min + (self.dbp_max - self.dbp_min) * sig[:, 1:2]
        
        return torch.cat([sbp_pred, dbp_pred], dim=1)

class BBPNet(nn.Module):
    """
    Blood Pressure estimation network (BBP-Net) ingesting the 6xT multi-site derivative tensor.
    """
    def __init__(self, in_channels=6, feat_dim=128, demo_dim=0, use_scaled_sigmoid=True):
        super(BBPNet, self).__init__()
        self.use_scaled_sigmoid = use_scaled_sigmoid
        
        # Spatial-temporal feature extractor with dilated convolutions for long receptive field
        self.conv_in = nn.Sequential(
            nn.Conv1d(in_channels, 32, kernel_size=7, stride=1, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=7, stride=2, padding=3, dilation=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, feat_dim, kernel_size=5, stride=2, padding=2, dilation=2),
            nn.BatchNorm1d(feat_dim),
            nn.ReLU()
        )

        # Cross-channel Pulse Wave Transit attention
        self.attn = nn.MultiheadAttention(embed_dim=feat_dim, num_heads=4, batch_first=True)
        
        # Decoupled regression heads
        self.sbp_head = nn.Sequential(
            nn.Linear(feat_dim + demo_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )
        self.dbp_head = nn.Sequential(
            nn.Linear(feat_dim + demo_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )

        if use_scaled_sigmoid:
            self.scaler = ScaledSigmoidBP()
        else:
            self.scaler = None

    def forward(self, x_6xt, demo=None):
        """
        Args:
            x_6xt: Tensor of shape (B, 6, T) containing [y_f, y_a, y'_f, y'_a, y''_f, y''_a].
            demo: Optional demographic tensor (B, demo_dim).
        """
        feat = self.conv_in(x_6xt).permute(0, 2, 1) # (B, T_down, 128)
        attn_out, _ = self.attn(feat, feat, feat)
        pooled = torch.mean(feat + attn_out, dim=1) # (B, 128)

        if demo is not None:
            fused = torch.cat([pooled, demo], dim=1)
        else:
            fused = pooled

        raw_sbp = self.sbp_head(fused)
        raw_dbp = self.dbp_head(fused)
        raw_bp = torch.cat([raw_sbp, raw_dbp], dim=1)

        if self.scaler is not None:
            return self.scaler(raw_bp)
        return raw_bp
