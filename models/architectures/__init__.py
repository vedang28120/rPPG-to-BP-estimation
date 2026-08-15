"""
Neural Network Architectures Package
Contains:
  - MODEL-06 Dual-Branch ResNet + BiGRU + MHSA
  - Bayesian ResNet-BiGRU with MC Dropout & Heteroscedastic NLL (U-FaceBP)
  - Cross-Modal PPG-Guided Alignment Models (ALIVE)
  - Dual-Site Phase-Shifted BBP-Net with Scaled Sigmoid Bounds
  - Baseline Demographic MLPs and Legacy LSTMs
"""

from .resnet_bigru_attn import ResidualBlock1D, DualBranchResNetBiGRUAttn
from .bayesian_ufacebp import (
    BayesianResidualBlock1D,
    BayesianResNetBiGRU,
    heteroscedastic_nll_loss,
    UncertaintyDrivenAggregator
)
from .alive_alignment import PPGEncoderTCN, ALIVEAlignmentModel, pearson_correlation_loss
from .drp_bbp_net import BBPNet, ScaledSigmoidBP
from .demo_mlp import DemoOnlyMLP
from .legacy_lstm import LegacyPPGLSTM

__all__ = [
    "ResidualBlock1D",
    "DualBranchResNetBiGRUAttn",
    "BayesianResidualBlock1D",
    "BayesianResNetBiGRU",
    "heteroscedastic_nll_loss",
    "UncertaintyDrivenAggregator",
    "PPGEncoderTCN",
    "ALIVEAlignmentModel",
    "pearson_correlation_loss",
    "BBPNet",
    "ScaledSigmoidBP",
    "DemoOnlyMLP",
    "LegacyPPGLSTM"
]
