"""
Uncertainty-Aware Bayesian Multi-Modal Fusion (U-FaceBP Paradigm)
Reference: U-FaceBP Framework (Nature / IEEE TBME).
Implements:
  1. Bayesian ResNet-BiGRU with Monte Carlo (MC) Dropout layers.
  2. Heteroscedastic Aleatoric Loss (Predictive Mean + Log-Variance Heads).
  3. Epistemic vs Aleatoric Uncertainty Quantification over T=10 stochastic forward passes.
  4. Uncertainty-Driven Aggregator (UDA) for multi-modal dynamic weighting.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class BayesianResidualBlock1D(nn.Module):
    """
    1D Residual Block with integrated Monte Carlo Dropout for Bayesian uncertainty approximation.
    """
    def __init__(self, in_channels, out_channels, kernel_size=5, stride=1, dilation=1, dropout_rate=0.2):
        super(BayesianResidualBlock1D, self).__init__()
        padding = ((kernel_size - 1) * dilation) // 2
        self.conv1 = nn.Conv1d(
            in_channels, out_channels,
            kernel_size=kernel_size, stride=stride, padding=padding, dilation=dilation, bias=False
        )
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.dropout = nn.Dropout(p=dropout_rate)
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

class BayesianResNetBiGRU(nn.Module):
    """
    Bayesian neural network estimating both predictive blood pressure and heteroscedastic uncertainty.
    """
    def __init__(self, in_channels=1, demo_dim=3, dropout_rate=0.2, use_separate_heads=True):
        super(BayesianResNetBiGRU, self).__init__()
        self.demo_dim = demo_dim
        self.dropout_rate = dropout_rate
        self.use_separate_heads = use_separate_heads

        # Dual-branch encoder
        self.branch1 = nn.Sequential(
            BayesianResidualBlock1D(in_channels, 32, kernel_size=5, stride=2, dropout_rate=dropout_rate),
            BayesianResidualBlock1D(32, 64, kernel_size=5, stride=2, dropout_rate=dropout_rate),
            BayesianResidualBlock1D(64, 128, kernel_size=5, stride=2, dropout_rate=dropout_rate)
        )
        self.branch2 = nn.Sequential(
            BayesianResidualBlock1D(in_channels, 32, kernel_size=11, stride=2, dilation=1, dropout_rate=dropout_rate),
            BayesianResidualBlock1D(32, 64, kernel_size=11, stride=2, dilation=2, dropout_rate=dropout_rate),
            BayesianResidualBlock1D(64, 128, kernel_size=11, stride=2, dilation=2, dropout_rate=dropout_rate)
        )

        # BiGRU with Dropout
        self.gru = nn.GRU(
            input_size=256,
            hidden_size=64,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout_rate
        )
        self.attn = nn.MultiheadAttention(embed_dim=128, num_heads=4, batch_first=True, dropout=dropout_rate)

        # Demographic encoder
        if demo_dim > 0:
            self.demo_encoder = nn.Sequential(
                nn.Linear(demo_dim, 32),
                nn.ReLU(),
                nn.Dropout(p=dropout_rate),
                nn.Linear(32, 32),
                nn.ReLU()
            )
            fused_dim = 128 + 32
        else:
            self.demo_encoder = None
            fused_dim = 128

        # Heteroscedastic Heads: Output [Mean (mu), Log-Variance (s = log(sigma^2))]
        # SBP Head outputs (mu_sbp, log_var_sbp)
        self.sbp_mean_head = nn.Sequential(
            nn.Linear(fused_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 1)
        )
        self.sbp_var_head = nn.Sequential(
            nn.Linear(fused_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 1)
        )

        # DBP Head outputs (mu_dbp, log_var_dbp)
        self.dbp_mean_head = nn.Sequential(
            nn.Linear(fused_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 1)
        )
        self.dbp_var_head = nn.Sequential(
            nn.Linear(fused_dim, 64),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(64, 1)
        )

    def forward(self, wave, demo=None):
        """
        Returns:
            mu: Tensor of shape (B, 2) containing [mu_sbp, mu_dbp]
            log_var: Tensor of shape (B, 2) containing [log_var_sbp, log_var_dbp]
        """
        b1 = self.branch1(wave)
        b2 = self.branch2(wave)
        feat = torch.cat([b1, b2], dim=1).permute(0, 2, 1)

        gru_out, _ = self.gru(feat)
        attn_out, _ = self.attn(gru_out, gru_out, gru_out)
        fused_seq = gru_out + attn_out

        pooled = torch.mean(fused_seq, dim=1)

        if self.demo_encoder is not None:
            if demo is None:
                demo = torch.zeros(pooled.size(0), self.demo_dim, device=pooled.device)
            demo_feat = self.demo_encoder(demo)
            fused = torch.cat([pooled, demo_feat], dim=1)
        else:
            fused = pooled

        mu_sbp = self.sbp_mean_head(fused)
        log_var_sbp = self.sbp_var_head(fused)
        
        mu_dbp = self.dbp_mean_head(fused)
        log_var_dbp = self.dbp_var_head(fused)

        mu = torch.cat([mu_sbp, mu_dbp], dim=1)
        log_var = torch.cat([log_var_sbp, log_var_dbp], dim=1)
        
        return mu, log_var

    def predict_with_uncertainty(self, wave, demo=None, num_samples=10):
        """
        Executes Monte Carlo Dropout sampling over T stochastic passes.
        
        Returns:
            pred_mean: (B, 2) Expected SBP/DBP
            aleatoric_unc: (B, 2) Data observation uncertainty (sigma^2)
            epistemic_unc: (B, 2) Model epistemic uncertainty (variance across MC runs)
        """
        self.train() # Keep dropout active
        
        means = []
        variances = []
        
        with torch.no_grad():
            for _ in range(num_samples):
                mu_sample, log_var_sample = self.forward(wave, demo)
                var_sample = torch.exp(log_var_sample)
                means.append(mu_sample.unsqueeze(0))
                variances.append(var_sample.unsqueeze(0))
                
        means_tensor = torch.cat(means, dim=0)       # (T, B, 2)
        variances_tensor = torch.cat(variances, dim=0) # (T, B, 2)
        
        pred_mean = torch.mean(means_tensor, dim=0)
        aleatoric_unc = torch.mean(variances_tensor, dim=0)
        epistemic_unc = torch.var(means_tensor, dim=0)
        
        return pred_mean, aleatoric_unc, epistemic_unc

def heteroscedastic_nll_loss(y_true, y_pred_mean, log_var):
    """
    Computes Gaussian Negative Log-Likelihood Loss:
    L = 0.5 * exp(-s) * ||y - y_hat||^2 + 0.5 * s
    where s = log(sigma^2)
    """
    precision = torch.exp(-log_var)
    sq_err = (y_true - y_pred_mean) ** 2
    loss = 0.5 * precision * sq_err + 0.5 * log_var
    return torch.mean(loss)

class UncertaintyDrivenAggregator(nn.Module):
    """
    Fuses multi-branch predictions dynamically weighted by their inverse total uncertainties:
    w_m = softmax(-s_total_m)
    """
    def __init__(self):
        super(UncertaintyDrivenAggregator, self).__init__()

    def forward(self, predictions_list, uncertainties_list):
        """
        Args:
            predictions_list: List of tensors [(B, 2), ...] from rPPG, PPG, and Image branches.
            uncertainties_list: List of total uncertainty tensors [(B, 2), ...].
        """
        stacked_preds = torch.stack(predictions_list, dim=1) # (B, M, 2)
        stacked_unc = torch.stack(uncertainties_list, dim=1)  # (B, M, 2)

        weights = F.softmax(-stacked_unc, dim=1)              # (B, M, 2)
        fused_output = torch.sum(weights * stacked_preds, dim=1) # (B, 2)
        
        return fused_output, weights
