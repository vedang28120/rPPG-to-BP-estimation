"""
Legacy Recurrent Neural Network (LSTM) Architecture
Keras/PyTorch compatible definition for the pre-trained MIMIC-III multi-layer LSTM model.
"""

import torch
import torch.nn as nn

class LegacyPPGLSTM(nn.Module):
    """
    Multi-layer LSTM network accepting 875-sample 125 Hz normalized PPG waveforms.
    """
    def __init__(self, input_dim=1, hidden_dim=64, num_layers=2, output_dim=2):
        super(LegacyPPGLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)  # [SBP, DBP]
        )

    def forward(self, x):
        # x shape: (B, L, 1)
        out, (hn, cn) = self.lstm(x)
        # Use final time step hidden representation
        last_hidden = out[:, -1, :]
        return self.fc(last_hidden)
