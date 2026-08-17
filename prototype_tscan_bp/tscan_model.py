"""
PyTorch Implementation of TS-CAN / MTTS-CAN
Exact architectural match to NeurIPS 2020 MTTS-CAN by Xin Liu et al.
Loads pretrained weights directly from mtts_can.hdf5.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import h5py
import os

class TSM(nn.Module):
    """
    Temporal Shift Module (TSM) for PyTorch.
    Shifts 1/fold_div channels left and right along the temporal dimension.
    """
    def __init__(self, n_segment=10, fold_div=3):
        super(TSM, self).__init__()
        self.n_segment = n_segment
        self.fold_div = fold_div

    def forward(self, x):
        # x shape: (N * T, C, H, W)
        nt, c, h, w = x.size()
        n_batch = nt // self.n_segment
        x = x.view(n_batch, self.n_segment, c, h, w)
        fold = c // self.fold_div
        last_fold = c - (self.fold_div - 1) * fold
        
        # Split into 3 parts
        out1 = x[:, :, :fold, :, :]
        out2 = x[:, :, fold:2*fold, :, :]
        out3 = x[:, :, 2*fold:, :, :]
        
        # Shift left (part 1)
        padding_1 = torch.zeros_like(out1[:, -1:, :, :, :])
        out1_shifted = torch.cat([out1[:, 1:, :, :, :], padding_1], dim=1)
        
        # Shift right (part 2)
        padding_2 = torch.zeros_like(out2[:, :1, :, :, :])
        out2_shifted = torch.cat([padding_2, out2[:, :-1, :, :, :]], dim=1)
        
        # Concat along channel dimension
        out = torch.cat([out1_shifted, out2_shifted, out3], dim=2)
        return out.view(nt, c, h, w)


class AttentionMask(nn.Module):
    """
    Spatial Attention Mask Layer.
    Normalizes attention maps across height and width.
    """
    def __init__(self):
        super(AttentionMask, self).__init__()

    def forward(self, x):
        # x shape: (B, 1, H, W)
        xsum = torch.sum(x, dim=(2, 3), keepdim=True) + 1e-8
        _, _, h, w = x.size()
        return (x / xsum) * (h * w * 0.5)


class TSCAN_PyTorch(nn.Module):
    """
    Multi-Task Temporal Shift Convolutional Attention Network (MTTS-CAN) in PyTorch.
    Inputs:
      - motion_input: Normalized difference frames ΔS(t) shape (B*T, 3, 36, 36)
      - appearance_input: Raw video frames S(t) shape (B*T, 3, 36, 36)
    Outputs:
      - pulse_pred: 1D derivative of blood volume pulse (B*T, 1)
      - resp_pred: 1D derivative of respiration wave (B*T, 1)
    """
    def __init__(self, frame_depth=10):
        super(TSCAN_PyTorch, self).__init__()
        self.frame_depth = frame_depth

        # --- Appearance Branch ---
        # Stage 1: Conv(same) -> Conv(valid) -> 36x36 -> 36x36 -> 34x34
        self.app_conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.app_conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=0)
        self.app_mask1 = nn.Conv2d(32, 1, kernel_size=1, padding=0)
        self.attn1 = AttentionMask()

        # Stage 2: AvgPool(2x2) -> Conv(same) -> Conv(valid) -> 17x17 -> 17x17 -> 15x15
        self.app_conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.app_conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=0)
        self.app_mask2 = nn.Conv2d(64, 1, kernel_size=1, padding=0)
        self.attn2 = AttentionMask()

        # --- Motion Branch ---
        # Stage 1: TSM+Conv(same) -> TSM+Conv(valid) -> 36x36 -> 36x36 -> 34x34
        self.tsm1 = TSM(n_segment=frame_depth, fold_div=3)
        self.mot_conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.tsm2 = TSM(n_segment=frame_depth, fold_div=3)
        self.mot_conv2 = nn.Conv2d(32, 32, kernel_size=3, padding=0)

        # Stage 2: AvgPool(2x2) -> TSM+Conv(same) -> TSM+Conv(valid) -> 17x17 -> 17x17 -> 15x15
        self.tsm3 = TSM(n_segment=frame_depth, fold_div=3)
        self.mot_conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.tsm4 = TSM(n_segment=frame_depth, fold_div=3)
        self.mot_conv4 = nn.Conv2d(64, 64, kernel_size=3, padding=0)

        # --- Dense Heads ---
        # Feature map after Stage 2 AvgPool(2,2) with 15x15: floor(15/2) = 7x7.
        # Flattened feature dimension: 64 channels * 7 * 7 = 3136
        self.pulse_dense1 = nn.Linear(3136, 128)
        self.pulse_out = nn.Linear(128, 1)

        self.resp_dense1 = nn.Linear(3136, 128)
        self.resp_out = nn.Linear(128, 1)

    def forward(self, motion_x, app_x):
        # 1. Appearance Stage 1
        a1 = torch.tanh(self.app_conv1(app_x))
        a2 = torch.tanh(self.app_conv2(a1))
        mask1 = torch.sigmoid(self.app_mask1(a2))
        mask1 = self.attn1(mask1)

        # 2. Motion Stage 1
        m1 = self.tsm1(motion_x)
        m1 = torch.tanh(self.mot_conv1(m1))
        m2 = self.tsm2(m1)
        m2 = torch.tanh(self.mot_conv2(m2))
        
        # Gated Multiplicative Attention 1
        g1 = m2 * mask1
        d3 = F.avg_pool2d(g1, kernel_size=2, stride=2)
        d4 = F.dropout(d3, p=0.25, training=self.training)

        # 3. Appearance Stage 2 (downsample app feature map a2 with avgpool)
        r3 = F.avg_pool2d(a2, kernel_size=2, stride=2)
        r4 = F.dropout(r3, p=0.25, training=self.training)
        r5 = torch.tanh(self.app_conv3(r4))
        r6 = torch.tanh(self.app_conv4(r5))
        mask2 = torch.sigmoid(self.app_mask2(r6))
        mask2 = self.attn2(mask2)

        # 4. Motion Stage 2
        m3 = self.tsm3(d4)
        m3 = torch.tanh(self.mot_conv3(m3))
        m4 = self.tsm4(m3)
        m4 = torch.tanh(self.mot_conv4(m4))

        # Gated Multiplicative Attention 2
        g2 = m4 * mask2
        d7 = F.avg_pool2d(g2, kernel_size=2, stride=2)
        d8 = F.dropout(d7, p=0.25, training=self.training)

        # 5. Dense Flatten & Heads
        # In Keras channels-last (B, H, W, C), flatten orders by row, col, channel.
        # In PyTorch channels-first (B, C, H, W), permute to (B, H, W, C) before flatten.
        feat = d8.permute(0, 2, 3, 1).contiguous().view(d8.size(0), -1)

        # Pulse (BVP) Head
        h_pulse = F.dropout(torch.tanh(self.pulse_dense1(feat)), p=0.5, training=self.training)
        pulse_pred = self.pulse_out(h_pulse)

        # Respiration Head
        h_resp = F.dropout(torch.tanh(self.resp_dense1(feat)), p=0.5, training=self.training)
        resp_pred = self.resp_out(h_resp)

        return pulse_pred, resp_pred

    def load_from_hdf5(self, hdf5_path):
        """Loads weights from Keras mtts_can.hdf5 checkpoint directly into PyTorch."""
        with h5py.File(hdf5_path, 'r') as f:
            mw = f['model_weights']
            
            # Helper to copy Conv2D weight: Keras (H, W, InC, OutC) -> PyTorch (OutC, InC, H, W)
            def load_conv(layer, name):
                k = np.array(mw[name][name]['kernel:0'])
                b = np.array(mw[name][name]['bias:0'])
                layer.weight.data.copy_(torch.from_numpy(k.transpose(3, 2, 0, 1)))
                layer.bias.data.copy_(torch.from_numpy(b))
            
            # Helper to copy Linear weight: Keras (InF, OutF) -> PyTorch (OutF, InF)
            def load_linear(layer, name):
                k = np.array(mw[name][name]['kernel:0'])
                b = np.array(mw[name][name]['bias:0'])
                layer.weight.data.copy_(torch.from_numpy(k.T))
                layer.bias.data.copy_(torch.from_numpy(b))

            # Motion Conv layers
            load_conv(self.mot_conv1, 'conv2d')
            load_conv(self.mot_conv2, 'conv2d_1')
            load_conv(self.mot_conv3, 'conv2d_5')
            load_conv(self.mot_conv4, 'conv2d_6')

            # Appearance Conv layers
            load_conv(self.app_conv1, 'conv2d_2')
            load_conv(self.app_conv2, 'conv2d_3')
            load_conv(self.app_mask1, 'conv2d_4')
            load_conv(self.app_conv3, 'conv2d_7')
            load_conv(self.app_conv4, 'conv2d_8')
            load_conv(self.app_mask2, 'conv2d_9')

            # Dense Heads
            load_linear(self.pulse_dense1, 'dense')
            load_linear(self.pulse_out, 'output_1')
            load_linear(self.resp_dense1, 'dense_1')
            load_linear(self.resp_out, 'output_2')

        print(f"[OK] Successfully loaded and mapped weights from {hdf5_path} into PyTorch TS-CAN.")

def get_tscan_model(hdf5_path=None, device="cpu"):
    model = TSCAN_PyTorch(frame_depth=10)
    if hdf5_path and os.path.exists(hdf5_path):
        model.load_from_hdf5(hdf5_path)
    model.to(device)
    model.eval()
    return model

if __name__ == "__main__":
    h5_path = os.path.join(os.path.dirname(__file__), "checkpoints", "mtts_can.hdf5")
    model = get_tscan_model(h5_path)
    
    # Test forward pass with 10 frames of 36x36
    dummy_motion = torch.randn(10, 3, 36, 36)
    dummy_app = torch.randn(10, 3, 36, 36)
    with torch.no_grad():
        p, r = model(dummy_motion, dummy_app)
    print(f"Test inference output shape: pulse={p.shape}, resp={r.shape}")
