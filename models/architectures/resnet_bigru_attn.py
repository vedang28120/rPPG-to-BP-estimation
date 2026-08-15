"""
MODEL-06: Dual-Branch 1D-ResNet + BiGRU + Multi-Head Self-Attention Architecture
Reference: Gold Pipeline PPG-to-BP Progressive Architecture with Decoupled SBP/DBP Regression Heads,
Optional Monte Carlo (MC) Dropout, and Scaled Sigmoid Physiological Bounding.
"""

import torch
import torch.nn as nn
from .drp_bbp_net import ScaledSigmoidBP

class ResidualBlock1D(nn.Module):
    """
    1D Residual Convolutional Block with optional dilation and projection shortcuts.
    """
    def __init__(self, in_channels, out_channels, kernel_size=5, stride=1, dilation=1, dropout_rate=0.0):
        super(ResidualBlock1D, self).__init__()
        padding = ((kernel_size - 1) * dilation) // 2
        self.conv1 = nn.Conv1d(
            in_channels, out_channels,
            kernel_size=kernel_size, stride=stride, padding=padding, dilation=dilation, bias=False
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(p=dropout_rate) if dropout_rate > 0 else nn.Identity()
        self.conv2 = nn.Conv1d(
            out_channels, out_channels,
            kernel_size=kernel_size, stride=1, padding=padding, dilation=dilation, bias=False
        )
        self.bn2 = nn.BatchNorm1d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm1d(out_channels)
            )

    def forward(self, x):
        res = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.dropout(out)
        out = self.bn2(self.conv2(out))
        out += res
        return self.relu(out)

class DualBranchResNetBiGRUAttn(nn.Module):
    """
    Dual-Branch ResNet + BiGRU + MHSA + Demographic Fusion + Decoupled SBP/DBP Heads
    with optional MC Dropout and Scaled Sigmoid physiological bounding.
    """
    def __init__(
        self,
        in_channels=1,
        demo_dim=3,
        use_dual_branch=True,
        use_bigru=True,
        use_attn=True,
        use_demo=True,
        use_separate_heads=True,
        dropout_rate=0.2,
        use_scaled_sigmoid=False
    ):
        super(DualBranchResNetBiGRUAttn, self).__init__()
        self.demo_dim = demo_dim
        self.use_dual_branch = use_dual_branch
        self.use_bigru = use_bigru
        self.use_attn = use_attn
        self.use_demo = use_demo
        self.use_separate_heads = use_separate_heads
        self.use_scaled_sigmoid = use_scaled_sigmoid

        # Branch 1: Short temporal receptive field (kernel_size=5)
        self.branch1 = nn.Sequential(
            ResidualBlock1D(in_channels, 32, kernel_size=5, stride=2, dropout_rate=dropout_rate),
            ResidualBlock1D(32, 64, kernel_size=5, stride=2, dropout_rate=dropout_rate),
            ResidualBlock1D(64, 128, kernel_size=5, stride=2, dropout_rate=dropout_rate)
        )

        # Branch 2: Wide temporal receptive field (kernel_size=11, dilated)
        if use_dual_branch:
            self.branch2 = nn.Sequential(
                ResidualBlock1D(in_channels, 32, kernel_size=11, stride=2, dilation=1, dropout_rate=dropout_rate),
                ResidualBlock1D(32, 64, kernel_size=11, stride=2, dilation=2, dropout_rate=dropout_rate),
                ResidualBlock1D(64, 128, kernel_size=11, stride=2, dilation=2, dropout_rate=dropout_rate)
            )
            conv_out_channels = 256
        else:
            self.branch2 = None
            conv_out_channels = 128

        # BiGRU Layer
        if use_bigru:
            self.gru = nn.GRU(
                input_size=conv_out_channels,
                hidden_size=64,
                num_layers=2,
                batch_first=True,
                bidirectional=True,
                dropout=dropout_rate
            )
            gru_out_dim = 128  # 64 * 2
        else:
            self.gru = None
            gru_out_dim = conv_out_channels

        # Multi-Head Self-Attention Layer
        if use_attn:
            self.attn = nn.MultiheadAttention(embed_dim=gru_out_dim, num_heads=4, batch_first=True, dropout=dropout_rate)
        else:
            self.attn = None

        # Demographic MLP encoder
        if use_demo and demo_dim > 0:
            self.demo_encoder = nn.Sequential(
                nn.Linear(demo_dim, 32),
                nn.ReLU(),
                nn.Linear(32, 32),
                nn.ReLU()
            )
            fused_dim = gru_out_dim + 32
        else:
            self.demo_encoder = None
            fused_dim = gru_out_dim

        # Output Regression Heads
        if use_separate_heads:
            self.sbp_head = nn.Sequential(
                nn.Linear(fused_dim, 64),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 1)
            )
            self.dbp_head = nn.Sequential(
                nn.Linear(fused_dim, 64),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 1)
            )
        else:
            self.joint_head = nn.Sequential(
                nn.Linear(fused_dim, 64),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(64, 2)
            )

        if use_scaled_sigmoid:
            self.scaler = ScaledSigmoidBP()
        else:
            self.scaler = None

    def forward(self, wave, demo=None):
        # Wave shape: (B, C, L)
        b1 = self.branch1(wave)
        if self.use_dual_branch:
            b2 = self.branch2(wave)
            feat = torch.cat([b1, b2], dim=1)
        else:
            feat = b1

        # Permute for sequence processing: (B, L_down, C_feat)
        feat = feat.permute(0, 2, 1)

        if self.use_bigru:
            feat, _ = self.gru(feat)

        if self.use_attn:
            attn_out, _ = self.attn(feat, feat, feat)
            feat = feat + attn_out

        # Global average temporal pooling: (B, C_dim)
        pooled = torch.mean(feat, dim=1)

        # Fuse demographic covariates
        if self.use_demo and self.demo_encoder is not None:
            if demo is None:
                demo = torch.zeros(pooled.size(0), self.demo_dim, device=pooled.device)
            demo_feat = self.demo_encoder(demo)
            fused = torch.cat([pooled, demo_feat], dim=1)
        else:
            fused = pooled

        # Decoupled or Joint Regression
        if self.use_separate_heads:
            sbp = self.sbp_head(fused)
            dbp = self.dbp_head(fused)
            raw_out = torch.cat([sbp, dbp], dim=1)
        else:
            raw_out = self.joint_head(fused)

        if self.scaler is not None:
            return self.scaler(raw_out)
        return raw_out
