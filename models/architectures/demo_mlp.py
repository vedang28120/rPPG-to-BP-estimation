"""
MODEL-01: Demographics-Only MLP Baseline
Maps static demographic features (age, sex, BMI/height/weight) directly to SBP and DBP.
"""

import torch
import torch.nn as nn

class DemoOnlyMLP(nn.Module):
    def __init__(self, demo_dim=3):
        super(DemoOnlyMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(demo_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 2)  # Outputs [SBP, DBP]
        )

    def forward(self, wave, demo):
        # Ignores waveform and infers solely from demographic priors
        return self.net(demo)
