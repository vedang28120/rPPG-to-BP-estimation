"""
MODEL-06 Blood Pressure Estimation Engine
Interfaces with trained MODEL-06 PyTorch checkpoints (Phase 1 LDS, Phase 2 ALIVE, Phase 3 Bayesian)
to estimate SBP and DBP from rPPG waveforms and demographic inputs.
"""
import os
import torch
import numpy as np
from scipy.signal import resample
from models.architectures.resnet_bigru_attn import DualBranchResNetBiGRUAttn
from models.architectures.bayesian_ufacebp import BayesianResNetBiGRU

class BPEstimationEngine:
    def __init__(self, checkpoint_path=None, model_type="auto", device="cpu"):
        self.device = device
        self.checkpoint_path = checkpoint_path
        self.model_type = model_type
        self.model = None
        self._load_best_model()

    def _load_best_model(self):
        # Default priority list of best checkpoints
        candidate_paths = [
            self.checkpoint_path,
            r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase3_Bayesian.pth",
            r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase1_LDS.pth",
            r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase2_ALIVE.pth",
            os.path.join(os.path.dirname(__file__), "..", "models", "checkpoints", "MODEL-06-SepHead_original.pth")
        ]

        chosen_path = None
        for p in candidate_paths:
            if p and os.path.exists(p):
                chosen_path = p
                break

        if not chosen_path:
            raise FileNotFoundError("Could not find any valid MODEL-06 checkpoint file.")

        print(f"[*] Loading Blood Pressure Estimation model from: {chosen_path}")
        state_dict = torch.load(chosen_path, map_location=self.device, weights_only=False)

        # Detect architecture type from state_dict keys
        if "sbp_mean_head.0.weight" in state_dict:
            self.model_type = "bayesian"
            self.model = BayesianResNetBiGRU(in_channels=1, demo_dim=3)
            self.model.load_state_dict(state_dict)
            print("[OK] Loaded Phase 3: Uncertainty-Aware Bayesian ResNet-BiGRU model.")
        else:
            self.model_type = "deterministic"
            # Check if scaled sigmoid was used
            use_sigmoid = "sbp_head.4.sigmoid.weight" in state_dict or "sbp_sigmoid.sigmoid.weight" in state_dict or any("sigmoid" in k for k in state_dict)
            self.model = DualBranchResNetBiGRUAttn(
                in_channels=1, demo_dim=3,
                use_dual_branch=True, use_bigru=True, use_attn=True,
                use_demo=True, use_separate_heads=True,
                use_scaled_sigmoid=use_sigmoid
            )
            self.model.load_state_dict(state_dict, strict=False)
            print("[OK] Loaded MODEL-06 Separate-Head Deterministic model.")

        self.model.to(self.device)
        self.model.eval()

    def predict_bp(self, rppg_signal, source_fs=30.0, age=25.0, gender=1, bmi=22.0, window_sec=7.0):
        """
        Estimates SBP and DBP from extracted rPPG signal.
        Args:
            rppg_signal (np.ndarray): 1D continuous pulse waveform
            source_fs (float): Sampling frequency of rppg_signal
            age (float): Patient age in years
            gender (int/float): 1 for Male, 0 for Female
            bmi (float): Body Mass Index (weight_kg / height_m^2)
            window_sec (float): Analysis window duration in seconds (standard = 7.0s)
        Returns:
            dict with SBP, DBP, MAP, PP, and Uncertainty (if Bayesian)
        """
        # 1. Resample rPPG signal to 125 Hz standard rate
        target_fs = 125.0
        num_target_samples = int(len(rppg_signal) * (target_fs / source_fs))
        resampled_pulse = resample(rppg_signal, num_target_samples)

        # 2. Windowing (7-second window = 875 samples at 125 Hz)
        win_size = int(window_sec * target_fs)
        if len(resampled_pulse) < win_size:
            # Pad if shorter than window
            padded = np.pad(resampled_pulse, (0, win_size - len(resampled_pulse)), mode='reflect')
            windows = [padded]
        else:
            # Overlapping sliding windows (stride = 2 seconds)
            stride = int(2.0 * target_fs)
            windows = []
            for start in range(0, len(resampled_pulse) - win_size + 1, stride):
                windows.append(resampled_pulse[start : start + win_size])

        # 3. Z-score normalize each window
        norm_windows = []
        for w in windows:
            std_val = np.std(w)
            if std_val < 1e-6:
                std_val = 1e-6
            norm_w = (w - np.mean(w)) / std_val
            norm_windows.append(norm_w)

        # 4. Prepare batch tensors: (B, 1, win_size)
        wave_tensor = torch.tensor(np.array(norm_windows), dtype=torch.float32).unsqueeze(1).to(self.device)
        
        # Demographic vector: [age, gender, bmi]
        demo_vec = np.tile([float(age), float(gender), float(bmi)], (len(windows), 1))
        demo_tensor = torch.tensor(demo_vec, dtype=torch.float32).to(self.device)

        # 5. Run Model Inference
        with torch.no_grad():
            if self.model_type == "bayesian":
                mu, log_var = self.model(wave_tensor, demo_tensor)
                # mu: (B, 2) [SBP, DBP], log_var: (B, 2) [log(var_sbp), log(var_dbp)]
                sbp_preds = mu[:, 0].cpu().numpy()
                dbp_preds = mu[:, 1].cpu().numpy()
                sbp_vars = torch.exp(log_var[:, 0]).cpu().numpy()
                dbp_vars = torch.exp(log_var[:, 1]).cpu().numpy()
                
                sbp_std = float(np.mean(np.sqrt(np.maximum(0, sbp_vars))))
                dbp_std = float(np.mean(np.sqrt(np.maximum(0, dbp_vars))))
            else:
                preds = self.model(wave_tensor, demo_tensor)
                # preds: (B, 2) [SBP, DBP]
                if isinstance(preds, tuple):
                    sbp_preds = preds[0].cpu().numpy().flatten()
                    dbp_preds = preds[1].cpu().numpy().flatten()
                else:
                    sbp_preds = preds[:, 0].cpu().numpy()
                    dbp_preds = preds[:, 1].cpu().numpy()
                sbp_std = 0.0
                dbp_std = 0.0

        # Mean blood pressure across windows
        mean_sbp = float(np.mean(sbp_preds))
        mean_dbp = float(np.mean(dbp_preds))

        # Enforce physiological consistency: SBP > DBP
        if mean_sbp < mean_dbp:
            mean_sbp, mean_dbp = mean_dbp, mean_sbp

        map_val = mean_dbp + (mean_sbp - mean_dbp) / 3.0
        pp_val = mean_sbp - mean_dbp

        return {
            "sbp": round(mean_sbp, 1),
            "dbp": round(mean_dbp, 1),
            "map": round(map_val, 1),
            "pulse_pressure": round(pp_val, 1),
            "sbp_uncertainty_sd": round(sbp_std, 2),
            "dbp_uncertainty_sd": round(dbp_std, 2),
            "num_windows": len(windows),
            "model_type": self.model_type
        }
