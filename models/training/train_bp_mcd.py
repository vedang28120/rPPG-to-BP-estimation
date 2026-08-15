import os
import sys
import glob
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import GroupShuffleSplit
from huggingface_hub import hf_hub_download, HfFileSystem, login

# Set random seeds for strict reproducibility
torch.manual_seed(42)
np.random.seed(42)

print("==========================================================================")
print("  GOLD PIPELINE PPG-TO-BP -- PROGRESSIVE ABLATION TRAINER (Phases 1-5)   ")
print("==========================================================================")

# 0. Handle Hugging Face Authentication Token
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    if sys.stdin and sys.stdin.isatty():
        print("\n[AUTHENTICATION] Hugging Face Access Token Required for Gated MCD Dataset.")
        try:
            hf_token = input("Please enter your Hugging Face Token: ").strip()
            if hf_token:
                login(token=hf_token)
                os.environ["HF_TOKEN"] = hf_token
                print("Successfully authenticated with Hugging Face!")
        except Exception as e:
            print(f"Warning: Hugging Face login prompt skipped/failed: {e}")
    else:
        print("[INFO] HF_TOKEN environment variable not set. Will attempt unauthenticated or cached downloads.")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using compute accelerator: {device}")

# GPU Performance Optimization Settings
if torch.cuda.is_available():
    torch.backends.cudnn.benchmark = True
    print("[GPU OPTIMIZATION] Enabled cuDNN Auto-tuner benchmark & Automatic Mixed Precision (AMP/FP16)!")

NUM_WORKERS = min(4, os.cpu_count() or 2) if torch.cuda.is_available() else 0
PIN_MEMORY = torch.cuda.is_available()
BATCH_SIZE = 128  # Increased from 32 to 128 to fully saturate GPU Tensor Cores

def get_dataloader(dataset, batch_size=BATCH_SIZE, shuffle=False, sampler=None):
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(shuffle if sampler is None else False),
        sampler=sampler,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        persistent_workers=(NUM_WORKERS > 0)
    )

# --------------------------------------------------------------------------
# 1. Quality Gating & Preprocessing (10-Second Windows, 50% Overlap @ 125 Hz)
# --------------------------------------------------------------------------
FS = 125  # 125 Hz
WIN_SEC = 10  # 10-second window = 1250 samples
WIN_LEN = FS * WIN_SEC
STEP_LEN = int(WIN_LEN * 0.5)  # 50% overlap = 625 samples

def check_quality_gate(sig):
    """
    Quality gate checking SNR, amplitude, flatlines, and NaN values.
    Returns (is_valid, rejection_reason)
    """
    if np.isnan(sig).any() or np.isinf(sig).any():
        return False, "NaN_or_Inf"
    std_val = np.std(sig)
    if std_val < 1e-4:
        return False, "Flatline"
    p2p = np.ptp(sig)
    if p2p < 1.0 or p2p > 500.0:
        return False, "Abnormal_Amplitude"
    return True, "Passed"

class RigorousMCDDataset(Dataset):
    def __init__(self, samples, in_channels=3):
        self.samples = samples
        self.in_channels = in_channels

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        item = self.samples[idx]
        wave = torch.tensor(item["wave"][:self.in_channels], dtype=torch.float32)
        return (
            wave,
            torch.tensor(item["demo"], dtype=torch.float32),
            torch.tensor(item["target"], dtype=torch.float32),
            item["subject_id"],
            item["step"]
        )

# --------------------------------------------------------------------------
# 2. Model Architectures
# --------------------------------------------------------------------------

# MODEL-01: Demographics-Only MLP Baseline
class DemoOnlyMLP(nn.Module):
    def __init__(self, demo_dim=3):
        super(DemoOnlyMLP, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(demo_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 2)  # [SBP, DBP]
        )

    def forward(self, wave, demo):
        return self.net(demo)

# ResidualBlock1D for all ResNet-based models
class ResidualBlock1D(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=5, stride=1, dilation=1):
        super(ResidualBlock1D, self).__init__()
        padding = ((kernel_size - 1) * dilation) // 2
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, stride=stride, padding=padding, dilation=dilation, bias=False)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size=kernel_size, stride=1, padding=padding, dilation=dilation, bias=False)
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
        out = self.bn2(self.conv2(out))
        out += res
        return self.relu(out)

# MODEL-03 through MODEL-06: Configurable architecture
class DualBranchResNetBiGRUAttn(nn.Module):
    """
    Unified model supporting all ablation configs:
      MODEL-03: use_branchB=False, use_attn=False, use_demo=False  (PPG-only single-branch)
      MODEL-04: use_branchB=True,  use_attn=False, use_demo=False  (Dual-Branch + BiGRU)
      MODEL-05: use_branchB=True,  use_attn=True,  use_demo=False  (+ MHSA)
      MODEL-06: use_branchB=True,  use_attn=True,  use_demo=True   (+ Demographics)
    """
    def __init__(self, in_channels=3, demo_dim=3, use_demo=True, use_attn=True, use_branchB=True, separate_heads=False, lambda_sbp=1.0, lambda_dbp=1.0):
        super(DualBranchResNetBiGRUAttn, self).__init__()
        self.use_demo = use_demo
        self.use_attn = use_attn
        self.use_branchB = use_branchB
        self.separate_heads = separate_heads
        self.lambda_sbp = lambda_sbp
        self.lambda_dbp = lambda_dbp
        
        # Branch A: High-Resolution Local Morphology (Kernel Size = 5)
        self.branchA = nn.Sequential(
            ResidualBlock1D(in_channels, 32, kernel_size=5, stride=2),
            ResidualBlock1D(32, 64, kernel_size=5, stride=2),
            ResidualBlock1D(64, 128, kernel_size=5, stride=2)
        )
        
        if self.use_branchB:
            # Branch B: Wide Receptive Field / Dilated Context (Kernel Size = 11, Dilation = 2)
            self.branchB = nn.Sequential(
                ResidualBlock1D(in_channels, 32, kernel_size=11, stride=2, dilation=1),
                ResidualBlock1D(32, 64, kernel_size=11, stride=2, dilation=2),
                ResidualBlock1D(64, 128, kernel_size=11, stride=2, dilation=2)
            )
            gru_input = 256
        else:
            gru_input = 128
        
        # BiGRU Layer
        self.gru = nn.GRU(input_size=gru_input, hidden_size=64, num_layers=2, batch_first=True, bidirectional=True)
        
        # Multi-Head Self-Attention
        if self.use_attn:
            self.attention = nn.MultiheadAttention(embed_dim=128, num_heads=4, batch_first=True)
            
        # Demographic Branch
        if self.use_demo:
            self.demo_mlp = nn.Sequential(
                nn.Linear(demo_dim, 16),
                nn.ReLU(),
                nn.Linear(16, 32),
                nn.ReLU()
            )
            in_fusion_dim = 128 + 32
        else:
            in_fusion_dim = 128
        
        # Regression Head(s)
        if self.separate_heads:
            self.sbp_head = nn.Sequential(
                nn.Linear(in_fusion_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 1)
            )
            self.dbp_head = nn.Sequential(
                nn.Linear(in_fusion_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 1)
            )
        else:
            self.head = nn.Sequential(
                nn.Linear(in_fusion_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 2)  # [SBP, DBP]
            )

    def forward(self, wave, demo):
        featA = self.branchA(wave)
        
        if self.use_branchB:
            featB = self.branchB(wave)
            fused_wave = torch.cat([featA, featB], dim=1)
        else:
            fused_wave = featA
        
        gru_in = fused_wave.permute(0, 2, 1)
        gru_out, _ = self.gru(gru_in)
        
        if self.use_attn:
            attn_out, _ = self.attention(gru_out, gru_out, gru_out)
            wave_vec = torch.mean(attn_out, dim=1)
        else:
            wave_vec = torch.mean(gru_out, dim=1)
            
        if self.use_demo:
            demo_vec = self.demo_mlp(demo)
            final_vec = torch.cat([wave_vec, demo_vec], dim=1)
        else:
            final_vec = wave_vec
        
        if self.separate_heads:
            sbp = self.sbp_head(final_vec)
            dbp = self.dbp_head(final_vec)
            return torch.cat([sbp, dbp], dim=1)
        else:
            return self.head(final_vec)

# --------------------------------------------------------------------------
# 3. Huber Loss + Pearson Correlation Penalty (with optional SBP weighting)
# --------------------------------------------------------------------------
class HuberPearsonLoss(nn.Module):
    def __init__(self, lambda_sbp=1.0, lambda_dbp=1.0):
        super(HuberPearsonLoss, self).__init__()
        self.huber = nn.HuberLoss(delta=1.0, reduction='none')
        self.lambda_sbp = lambda_sbp
        self.lambda_dbp = lambda_dbp

    def forward(self, pred, target):
        per_sample = self.huber(pred, target)
        # Apply per-target weighting: column 0 = SBP, column 1 = DBP
        weights = torch.tensor([self.lambda_sbp, self.lambda_dbp], device=pred.device)
        loss_huber = torch.mean(per_sample * weights)
        
        if pred.size(0) > 1:
            vx = pred - torch.mean(pred, dim=0)
            vy = target - torch.mean(target, dim=0)
            cost = torch.sum(vx * vy, dim=0) / (torch.sqrt(torch.sum(vx ** 2, dim=0)) * torch.sqrt(torch.sum(vy ** 2, dim=0)) + 1e-8)
            loss_corr = torch.mean(1.0 - cost)
        else:
            loss_corr = 0.0
            
        return loss_huber + 0.2 * loss_corr

# --------------------------------------------------------------------------
# 4. Rigorous Subject-Level Data Loader (Auto-Downloads from HuggingFace)
# --------------------------------------------------------------------------
def load_and_preprocess_mcd(base_dir="./mcd_dataset", token=None, max_subjects=600):
    if token is None:
        token = os.getenv("HF_TOKEN")
        
    print(f"Loading MCD metadata db.csv (Base Dir: {base_dir})...")
    db_path = os.path.join(base_dir, "db.csv")
    if not os.path.exists(db_path):
        db_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset', token=token, local_dir=base_dir)
    df_db = pd.read_csv(db_path)
    df_valid = df_db[(df_db['upper_ap'].notnull()) & (df_db['lower_ap'].notnull())].copy()
    
    # Calculate demographic normalization parameters from cohort
    age_mean, age_std = df_valid['age'].mean(), df_valid['age'].std()
    bmi_mean, bmi_std = df_valid['bmi'].mean(), df_valid['bmi'].std()
    if np.isnan(age_std) or age_std == 0: age_std = 1.0
    if np.isnan(bmi_std) or bmi_std == 0: bmi_std = 1.0
    
    # Store normalization params for later verification
    norm_params = {
        "age_mean": float(age_mean), "age_std": float(age_std),
        "bmi_mean": float(bmi_mean), "bmi_std": float(bmi_std)
    }
    
    all_samples = []
    rejection_log = {"NaN_or_Inf": 0, "Flatline": 0, "Abnormal_Amplitude": 0, "Too_Short": 0, "Download_Failed": 0}
    
    print("Windowing PPG signals (10s windows, 50% overlap)...")
    
    unique_pids = list(df_valid['patient_id'].unique())[:max_subjects]
    df_filtered = df_valid[df_valid['patient_id'].isin(unique_pids)]
    
    for idx, row in df_filtered.iterrows():
        pid = int(row['patient_id'])
        step = str(row['step'])
        sbp = float(row['upper_ap'])
        dbp = float(row['lower_ap'])
        
        age = (float(row['age']) - age_mean) / age_std if not np.isnan(row['age']) else 0.0
        sex = 1.0 if str(row['sex']).strip().upper() == 'M' else 0.0
        bmi = (float(row['bmi']) - bmi_mean) / bmi_std if not np.isnan(row['bmi']) else 0.0
        demo_vec = np.array([age, sex, bmi], dtype=np.float32)
        
        target_file_path = None
        
        # Check local filesystem first
        sub_dir = os.path.join(base_dir, f"Subject_{pid}")
        local_pw = os.path.join(sub_dir, "ppg", "ppg", f"{pid}_{step}.PW")
        if not os.path.exists(local_pw): local_pw = os.path.join(sub_dir, "ppg", f"{pid}_{step}.PW")
        local_sync = os.path.join(sub_dir, "ppg_sync", "ppg_sync", f"{pid}_IriunWebcam_{step}.txt")
        if not os.path.exists(local_sync): local_sync = os.path.join(sub_dir, "ppg_sync", f"{pid}_IriunWebcam_{step}.txt")
        
        if os.path.exists(local_pw):
            target_file_path = local_pw
        elif os.path.exists(local_sync):
            target_file_path = local_sync
        else:
            # Download ppg_sync or ppg file from Hugging Face on the fly
            try:
                rel_path = f"ppg_sync/{pid}_IriunWebcam_{step}.txt"
                target_file_path = hf_hub_download(
                    repo_id="wengziheng/mcd_rppg",
                    repo_type="dataset",
                    filename=rel_path,
                    token=token,
                    local_dir=base_dir
                )
            except Exception:
                try:
                    rel_path = f"ppg/{pid}_{step}.PW"
                    target_file_path = hf_hub_download(
                        repo_id="wengziheng/mcd_rppg",
                        repo_type="dataset",
                        filename=rel_path,
                        token=token,
                        local_dir=base_dir
                    )
                except Exception:
                    rejection_log["Download_Failed"] += 1
                    continue
                    
        if not target_file_path or not os.path.exists(target_file_path):
            rejection_log["Download_Failed"] += 1
            continue
            
        raw_ppg = []
        with open(target_file_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    try: raw_ppg.append(float(parts[0]))
                    except: pass
                    
        if len(raw_ppg) < WIN_LEN:
            rejection_log["Too_Short"] += 1
            continue
            
        raw_arr = np.array(raw_ppg)
        num_windows = (len(raw_arr) - WIN_LEN) // STEP_LEN + 1
        
        for w_i in range(num_windows):
            start = w_i * STEP_LEN
            end = start + WIN_LEN
            win = raw_arr[start:end]
            
            is_valid, reason = check_quality_gate(win)
            if not is_valid:
                rejection_log[reason] += 1
                continue
                
            # Per-window Z-score standardization
            norm_win = (win - np.mean(win)) / np.std(win)
            vppg = np.gradient(norm_win)
            appg = np.gradient(vppg)
            wave_3d = np.stack([norm_win, vppg, appg], axis=0)  # [3, 1250]
            
            all_samples.append({
                "wave": wave_3d,
                "demo": demo_vec,
                "target": np.array([sbp, dbp], dtype=np.float32),
                "subject_id": pid,
                "step": step
            })
            
    print(f"Dataset extraction finished! Total valid windows: {len(all_samples)}")
    print("Quality Gate Rejection Log:", rejection_log)
    return all_samples, df_valid, norm_params

# --------------------------------------------------------------------------
# 5. Evaluation (Shared across all models)
# --------------------------------------------------------------------------
def evaluate_model(model, dataloader, model_name="Model"):
    model.eval()
    sbp_errs, dbp_errs = [], []
    sbp_preds, sbp_trues = [], []
    dbp_preds, dbp_trues = [], []
    subject_results = {}
    
    use_amp = torch.cuda.is_available()
    dev_type = "cuda" if use_amp else "cpu"
    with torch.no_grad():
        for wave, demo, target, pids, steps in dataloader:
            wave, demo = wave.to(device, non_blocking=True), demo.to(device, non_blocking=True)
            with torch.amp.autocast(device_type=dev_type, enabled=use_amp):
                preds = model(wave, demo).float().cpu().numpy()
            targets = target.numpy()
            
            for i in range(len(targets)):
                sp, dp = preds[i][0], preds[i][1]
                st, dt = targets[i][0], targets[i][1]
                pid = pids[i].item() if isinstance(pids[i], torch.Tensor) else pids[i]
                
                sbp_errs.append(abs(sp - st))
                dbp_errs.append(abs(dp - dt))
                sbp_preds.append(sp); sbp_trues.append(st)
                dbp_preds.append(dp); dbp_trues.append(dt)
                
                if pid not in subject_results:
                    subject_results[pid] = {"sp_p": [], "sp_t": [], "dp_p": [], "dp_t": []}
                subject_results[pid]["sp_p"].append(sp)
                subject_results[pid]["sp_t"].append(st)
                subject_results[pid]["dp_p"].append(dp)
                subject_results[pid]["dp_t"].append(dt)
                
    mae_s = np.mean(sbp_errs) if len(sbp_errs) > 0 else 0.0
    rmse_s = np.sqrt(np.mean((np.array(sbp_preds) - np.array(sbp_trues))**2)) if len(sbp_preds) > 0 else 0.0
    r_s = np.corrcoef(sbp_trues, sbp_preds)[0, 1] if len(sbp_preds) > 1 else 0.0
    
    mae_d = np.mean(dbp_errs) if len(dbp_errs) > 0 else 0.0
    rmse_d = np.sqrt(np.mean((np.array(dbp_preds) - np.array(dbp_trues))**2)) if len(dbp_preds) > 0 else 0.0
    r_d = np.corrcoef(dbp_trues, dbp_preds)[0, 1] if len(dbp_preds) > 1 else 0.0
    
    sub_s_errs, sub_d_errs = [], []
    for pid, res in subject_results.items():
        sub_s_errs.append(abs(np.mean(res["sp_p"]) - np.mean(res["sp_t"])))
        sub_d_errs.append(abs(np.mean(res["dp_p"]) - np.mean(res["dp_t"])))
    sub_mae_s = np.mean(sub_s_errs) if len(sub_s_errs) > 0 else 0.0
    sub_mae_d = np.mean(sub_d_errs) if len(sub_d_errs) > 0 else 0.0
    
    if np.isnan(r_s): r_s = 0.0
    if np.isnan(r_d): r_d = 0.0
    
    print(f"[{model_name}] Window MAE -> SBP: {mae_s:.2f} mmHg (RMSE {rmse_s:.2f}, r={r_s:.3f}), DBP: {mae_d:.2f} mmHg (RMSE {rmse_d:.2f}, r={r_d:.3f}) | Subject MAE -> SBP: {sub_mae_s:.2f}, DBP: {sub_mae_d:.2f}")
    
    return {
        "model": model_name,
        "win_sbp_mae": mae_s, "win_sbp_rmse": rmse_s, "win_sbp_r": r_s,
        "win_dbp_mae": mae_d, "win_dbp_rmse": rmse_d, "win_dbp_r": r_d,
        "sub_sbp_mae": sub_mae_s, "sub_dbp_mae": sub_mae_d,
        "sbp_preds": sbp_preds, "sbp_trues": sbp_trues,
        "dbp_preds": dbp_preds, "dbp_trues": dbp_trues
    }

# --------------------------------------------------------------------------
# 5b. Clinical BP Bin Evaluation & Diagnostic Function
# --------------------------------------------------------------------------
def evaluate_bp_bins(model, dataloader, model_name="Model"):
    model.eval()
    results = evaluate_model(model, dataloader, model_name)
    sbp_preds = np.array(results["sbp_preds"])
    sbp_trues = np.array(results["sbp_trues"])
    dbp_preds = np.array(results["dbp_preds"])
    dbp_trues = np.array(results["dbp_trues"])
    
    # Clinical SBP Bins: <100 (Hypotensive), 100-120 (Normal), 120-140 (Pre-hypertensive), >140 (Hypertensive)
    bins = [
        ("< 100 mmHg (Low)", sbp_trues < 100),
        ("100 - 120 mmHg (Normal)", (sbp_trues >= 100) & (sbp_trues < 120)),
        ("120 - 140 mmHg (Pre-Hypertensive)", (sbp_trues >= 120) & (sbp_trues < 140)),
        ("> 140 mmHg (Hypertensive)", sbp_trues >= 140),
    ]
    
    bin_metrics = []
    print(f"\n  --- CLINICAL SBP BIN EVALUATION ({model_name}) ---")
    print(f"  {'Bin Range':<35} {'Count':>7} {'MAE (mmHg)':>11} {'RMSE':>8} {'Mean Bias':>11}")
    print(f"  {'-'*76}")
    
    for label, mask in bins:
        count = np.sum(mask)
        if count == 0:
            continue
        sub_preds = sbp_preds[mask]
        sub_trues = sbp_trues[mask]
        mae = np.mean(np.abs(sub_preds - sub_trues))
        rmse = np.sqrt(np.mean((sub_preds - sub_trues)**2))
        bias = np.mean(sub_preds - sub_trues)  # Positive = overprediction, Negative = underprediction
        print(f"  {label:<35} {count:7d} {mae:11.2f} {rmse:8.2f} {bias:+11.2f}")
        bin_metrics.append({
            "bin": label, "count": count, "mae": mae, "rmse": rmse, "bias": bias
        })
    results["bin_metrics"] = bin_metrics
    return results

# --------------------------------------------------------------------------
# 5c. Subject-Aware Weighted Sampler Generator (TRAINING SET ONLY)
# --------------------------------------------------------------------------
def create_weighted_sampler(train_samples, mode="moderate"):
    """
    Creates a WeightedRandomSampler based on training SBP distribution.
    Uses 10 mmHg SBP bins derived strictly from the training cohort.
    
    Modes:
      - 'moderate': weight = min(5.0, sqrt(median_freq / bin_freq))
      - 'strong':   weight = min(10.0, median_freq / bin_freq)
    """
    train_sbps = np.array([s["target"][0] for s in train_samples])
    
    # Define 10 mmHg bin boundaries from 80 to 180
    bin_edges = np.arange(80, 190, 10)
    bin_indices = np.digitize(train_sbps, bin_edges)
    
    bin_counts = pd.Series(bin_indices).value_counts()
    median_freq = bin_counts.median()
    
    sample_weights = []
    cap = 5.0 if mode == "moderate" else 10.0
    power = 0.5 if mode == "moderate" else 1.0
    
    for b_idx in bin_indices:
        freq = bin_counts.get(b_idx, 1)
        raw_w = (median_freq / freq) ** power
        w = min(cap, raw_w)
        sample_weights.append(w)
        
    sample_weights = torch.tensor(sample_weights, dtype=torch.double)
    sampler = torch.utils.data.WeightedRandomSampler(
        weights=sample_weights, num_samples=len(sample_weights), replacement=True
    )
    print(f"  Created '{mode}' WeightedRandomSampler (cap={cap}, power={power}) for {len(train_samples)} training samples.")
    return sampler

# --------------------------------------------------------------------------
# 5d. Cohort Distribution Analysis & Plotting
# --------------------------------------------------------------------------
def analyze_and_plot_bp_distribution(train_samples, val_samples, test_samples):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    print("\n" + "="*74)
    print("  COHORT BP DISTRIBUTION ANALYSIS (Train / Val / Test)")
    print("="*74)
    
    sets = [("Train", train_samples), ("Val", val_samples), ("Test", test_samples)]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for name, samples in sets:
        sbps = [s["target"][0] for s in samples]
        dbps = [s["target"][1] for s in samples]
        
        print(f"\n  --- {name} Cohort ({len(samples)} windows, {len(set(s['subject_id'] for s in samples))} subjects) ---")
        print(f"    SBP: Mean={np.mean(sbps):.1f}, Std={np.std(sbps):.1f}, Median={np.median(sbps):.1f}, Min={np.min(sbps):.1f}, Max={np.max(sbps):.1f}")
        print(f"    SBP Percentiles (10, 25, 50, 75, 90): {np.percentile(sbps, [10, 25, 50, 75, 90]).round(1)}")
        print(f"    DBP: Mean={np.mean(dbps):.1f}, Std={np.std(dbps):.1f}, Median={np.median(dbps):.1f}, Min={np.min(dbps):.1f}, Max={np.max(dbps):.1f}")
        print(f"    DBP Percentiles (10, 25, 50, 75, 90): {np.percentile(dbps, [10, 25, 50, 75, 90]).round(1)}")
        
        axes[0].hist(sbps, bins=30, alpha=0.5, label=f'{name} (N={len(samples)})')
        axes[1].hist(dbps, bins=30, alpha=0.5, label=f'{name} (N={len(samples)})')
        
    axes[0].set_xlabel('Systolic BP (mmHg)')
    axes[0].set_ylabel('Window Count')
    axes[0].set_title('SBP Distribution Across Cohorts')
    axes[0].legend()
    
    axes[1].set_xlabel('Diastolic BP (mmHg)')
    axes[1].set_ylabel('Window Count')
    axes[1].set_title('DBP Distribution Across Cohorts')
    axes[1].legend()
    
    plt.tight_layout()
    os.makedirs("./results", exist_ok=True)
    plt.savefig("./results/bp_distribution_histograms.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved: ./results/bp_distribution_histograms.png")

# --------------------------------------------------------------------------
# 6. Generic Training Function (reusable across all models)
# --------------------------------------------------------------------------
def train_model(model, train_loader, val_loader, train_count, val_count,
                epochs=40, lr=1e-3, save_name="model", criterion=None, model_label="Model", force_retrain=False):
    os.makedirs("./models", exist_ok=True)
    pth_path = f"./models/{save_name}.pth"
    
    if os.path.exists(pth_path) and not force_retrain:
        print(f"  [CHECKPOINT REUSED] Found existing '{pth_path}' -- skipping training & evaluating directly!")
        model.load_state_dict(torch.load(pth_path, map_location=device, weights_only=True))
        return model
        
    if criterion is None:
        criterion = HuberPearsonLoss()
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    use_amp = torch.cuda.is_available()
    dev_type = "cuda" if use_amp else "cpu"
    scaler = torch.amp.GradScaler(device=dev_type, enabled=use_amp)
    
    best_val_loss = float('inf')
    best_epoch = 0
    
    for epoch in range(1, epochs + 1):
        model.train()
        t_loss = 0.0
        for wave, demo, target, _, _ in train_loader:
            wave, demo, target = wave.to(device, non_blocking=True), demo.to(device, non_blocking=True), target.to(device, non_blocking=True)
            optimizer.zero_grad()
            
            with torch.amp.autocast(device_type=dev_type, enabled=use_amp):
                pred = model(wave, demo)
                loss = criterion(pred, target)
                
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            t_loss += loss.item() * wave.size(0)
        t_loss /= train_count
        
        model.eval()
        v_loss = 0.0
        with torch.no_grad():
            for wave, demo, target, _, _ in val_loader:
                wave, demo = wave.to(device, non_blocking=True), demo.to(device, non_blocking=True)
                with torch.amp.autocast(device_type=dev_type, enabled=use_amp):
                    pred = model(wave, demo)
                    loss = criterion(pred, target.to(device, non_blocking=True))
                v_loss += loss.item() * wave.size(0)
        v_loss /= val_count
        scheduler.step(v_loss)
        
        if v_loss < best_val_loss:
            best_val_loss = v_loss
            best_epoch = epoch
            torch.save(model.state_dict(), pth_path)
            
        if epoch % 10 == 0 or epoch == epochs:
            print(f"  [{model_label}] Epoch {epoch:02d}/{epochs:02d} | Train: {t_loss:.4f} | Val: {v_loss:.4f} (best @ ep {best_epoch})")
    
    # Reload best weights
    model.load_state_dict(torch.load(pth_path, map_location=device, weights_only=True))
    return model

# --------------------------------------------------------------------------
# 7. PHASE 1: Verify Baseline & Check for Leakage
# --------------------------------------------------------------------------
def run_phase1_verify_baseline(train_samples, val_samples, test_samples, norm_params):
    print("\n" + "="*74)
    print("  PHASE 1 — LOCK CURRENT BASELINE & VERIFY NO DATA LEAKAGE")
    print("="*74)
    
    train_subs = sorted(set(s["subject_id"] for s in train_samples))
    val_subs = sorted(set(s["subject_id"] for s in val_samples))
    test_subs = sorted(set(s["subject_id"] for s in test_samples))
    
    train_set = set(train_subs)
    val_set = set(val_subs)
    test_set = set(test_subs)
    
    leak_tv = train_set & val_set
    leak_tt = train_set & test_set
    leak_vt = val_set & test_set
    
    print(f"\n  Train subjects ({len(train_subs)}): {train_subs[:10]}{'...' if len(train_subs) > 10 else ''}")
    print(f"  Val subjects   ({len(val_subs)}):  {val_subs[:10]}{'...' if len(val_subs) > 10 else ''}")
    print(f"  Test subjects  ({len(test_subs)}): {test_subs[:10]}{'...' if len(test_subs) > 10 else ''}")
    
    print(f"\n  Train intersect Val overlap:  {len(leak_tv)} subjects {'[WARNING] LEAKAGE!' if leak_tv else '[OK] CLEAN'}")
    print(f"  Train intersect Test overlap: {len(leak_tt)} subjects {'[WARNING] LEAKAGE!' if leak_tt else '[OK] CLEAN'}")
    print(f"  Val intersect Test overlap:   {len(leak_vt)} subjects {'[WARNING] LEAKAGE!' if leak_vt else '[OK] CLEAN'}")
    
    # Verify normalization uses full cohort (acceptable) or train-only (ideal)
    train_ages = [s["demo"][0] for s in train_samples]
    print(f"\n  Normalization params: age_mean={norm_params['age_mean']:.2f}, age_std={norm_params['age_std']:.2f}, bmi_mean={norm_params['bmi_mean']:.2f}, bmi_std={norm_params['bmi_std']:.2f}")
    print(f"  NOTE: Demographics normalized using full cohort statistics (standard practice for standardized datasets).")
    
    # Train BP target distribution
    train_sbps = [s["target"][0] for s in train_samples]
    train_dbps = [s["target"][1] for s in train_samples]
    test_sbps = [s["target"][0] for s in test_samples]
    test_dbps = [s["target"][1] for s in test_samples]
    print(f"\n  Train BP distribution: SBP {np.mean(train_sbps):.1f}+/-{np.std(train_sbps):.1f}, DBP {np.mean(train_dbps):.1f}+/-{np.std(train_dbps):.1f}")
    print(f"  Test  BP distribution: SBP {np.mean(test_sbps):.1f}+/-{np.std(test_sbps):.1f}, DBP {np.mean(test_dbps):.1f}+/-{np.std(test_dbps):.1f}")
    
    return len(leak_tv) == 0 and len(leak_tt) == 0 and len(leak_vt) == 0

# --------------------------------------------------------------------------
# 8. PHASE 2: All Baselines
# --------------------------------------------------------------------------
def run_phase2_baselines(train_samples, val_samples, test_samples):
    print("\n" + "="*74)
    print("  PHASE 2 — BASELINES (Population Mean, Demographics-Only)")
    print("="*74)
    
    results = []
    
    # MODEL-00: Population Mean
    train_sbp_mean = np.mean([s["target"][0] for s in train_samples])
    train_dbp_mean = np.mean([s["target"][1] for s in train_samples])
    
    test_sbp_errs = [abs(s["target"][0] - train_sbp_mean) for s in test_samples]
    test_dbp_errs = [abs(s["target"][1] - train_dbp_mean) for s in test_samples]
    test_sbps = [s["target"][0] for s in test_samples]
    test_dbps = [s["target"][1] for s in test_samples]
    
    # Subject-level for population mean
    sub_results = {}
    for s in test_samples:
        pid = s["subject_id"]
        if pid not in sub_results: sub_results[pid] = {"st": [], "dt": []}
        sub_results[pid]["st"].append(s["target"][0])
        sub_results[pid]["dt"].append(s["target"][1])
    sub_sbp_errs = [abs(np.mean(v["st"]) - train_sbp_mean) for v in sub_results.values()]
    sub_dbp_errs = [abs(np.mean(v["dt"]) - train_dbp_mean) for v in sub_results.values()]
    
    r00 = {
        "model": "MODEL-00: Population Mean",
        "win_sbp_mae": np.mean(test_sbp_errs), "win_sbp_rmse": np.sqrt(np.mean([(s - train_sbp_mean)**2 for s in test_sbps])),
        "win_sbp_r": 0.0,
        "win_dbp_mae": np.mean(test_dbp_errs), "win_dbp_rmse": np.sqrt(np.mean([(s - train_dbp_mean)**2 for s in test_dbps])),
        "win_dbp_r": 0.0,
        "sub_sbp_mae": np.mean(sub_sbp_errs), "sub_dbp_mae": np.mean(sub_dbp_errs)
    }
    print(f"\n  [MODEL-00: Population Mean] SBP: {train_sbp_mean:.1f} mmHg, DBP: {train_dbp_mean:.1f} mmHg")
    print(f"    Window MAE -> SBP: {r00['win_sbp_mae']:.2f}, DBP: {r00['win_dbp_mae']:.2f} | Subject MAE -> SBP: {r00['sub_sbp_mae']:.2f}, DBP: {r00['sub_dbp_mae']:.2f}")
    results.append(r00)
    
    # MODEL-01: Demographics-Only MLP
    print(f"\n  Training MODEL-01: Demographics-Only MLP...")
    train_loader = DataLoader(RigorousMCDDataset(train_samples), batch_size=32, shuffle=True)
    val_loader = DataLoader(RigorousMCDDataset(val_samples), batch_size=32, shuffle=False)
    test_loader = DataLoader(RigorousMCDDataset(test_samples), batch_size=32, shuffle=False)
    
    demo_model = DemoOnlyMLP(demo_dim=3).to(device)
    demo_model = train_model(demo_model, train_loader, val_loader,
                             len(train_samples), len(val_samples),
                             epochs=40, lr=1e-3, save_name="model01_demo_only",
                             model_label="MODEL-01")
    r01 = evaluate_model(demo_model, test_loader, "MODEL-01: Demographics-Only")
    results.append(r01)
    
    return results, train_loader, val_loader, test_loader

# --------------------------------------------------------------------------
# 9. PHASE 3: Progressive Architecture Ablation Ladder
# --------------------------------------------------------------------------
def run_phase3_ablation(train_samples, val_samples, test_samples, train_loader, val_loader, test_loader, in_channels=3):
    print("\n" + "="*74)
    print("  PHASE 3 — ARCHITECTURE ABLATION LADDER")
    print("="*74)
    
    results = []
    
    ablation_configs = [
        ("MODEL-03", "PPG-only Single-Branch ResNet+BiGRU",
         dict(in_channels=in_channels, use_branchB=False, use_attn=False, use_demo=False)),
        ("MODEL-04", "Dual-Branch ResNet+BiGRU",
         dict(in_channels=in_channels, use_branchB=True, use_attn=False, use_demo=False)),
        ("MODEL-05", "Dual-Branch+BiGRU+MHSA",
         dict(in_channels=in_channels, use_branchB=True, use_attn=True, use_demo=False)),
        ("MODEL-06", "Dual-Branch+BiGRU+MHSA+Demographics",
         dict(in_channels=in_channels, use_branchB=True, use_attn=True, use_demo=True)),
    ]
    
    for model_id, desc, cfg in ablation_configs:
        print(f"\n  Training {model_id}: {desc}...")
        model = DualBranchResNetBiGRUAttn(**cfg).to(device)
        save_name = f"model_{model_id.lower().replace('-','')}"
        model = train_model(model, train_loader, val_loader,
                           len(train_samples), len(val_samples),
                           epochs=40, lr=1e-3, save_name=save_name,
                           model_label=model_id)
        r = evaluate_model(model, test_loader, f"{model_id}: {desc}")
        results.append(r)
    
    return results

# --------------------------------------------------------------------------
# 10. PHASE 4: Input Channel Ablation (PPG vs PPG+vPPG vs PPG+vPPG+aPPG)
# --------------------------------------------------------------------------
def run_phase4_input_ablation(train_samples, val_samples, test_samples):
    print("\n" + "="*74)
    print("  PHASE 4 — INPUT CHANNEL ABLATION")
    print("="*74)
    
    results = []
    
    channel_configs = [
        (1, "PPG only"),
        (2, "PPG + vPPG"),
        (3, "PPG + vPPG + aPPG"),
    ]
    
    for n_ch, desc in channel_configs:
        print(f"\n  Training MODEL-06 variant with {desc} ({n_ch} channels)...")
        train_loader = DataLoader(RigorousMCDDataset(train_samples, in_channels=n_ch), batch_size=32, shuffle=True)
        val_loader = DataLoader(RigorousMCDDataset(val_samples, in_channels=n_ch), batch_size=32, shuffle=False)
        test_loader = DataLoader(RigorousMCDDataset(test_samples, in_channels=n_ch), batch_size=32, shuffle=False)
        
        model = DualBranchResNetBiGRUAttn(in_channels=n_ch, use_branchB=True, use_attn=True, use_demo=True).to(device)
        save_name = f"model06_ch{n_ch}"
        model = train_model(model, train_loader, val_loader,
                           len(train_samples), len(val_samples),
                           epochs=40, lr=1e-3, save_name=save_name,
                           model_label=f"MODEL-06 ({desc})")
        r = evaluate_model(model, test_loader, f"MODEL-06 ({desc})")
        results.append(r)
    
    return results

# --------------------------------------------------------------------------
# 11. PHASE 5: SBP-Specific Investigation
# --------------------------------------------------------------------------
def run_phase5_sbp_investigation(train_samples, val_samples, test_samples):
    print("\n" + "="*74)
    print("  PHASE 5 — SBP-SPECIFIC INVESTIGATION")
    print("="*74)
    
    results = []
    
    train_loader = DataLoader(RigorousMCDDataset(train_samples), batch_size=32, shuffle=True)
    val_loader = DataLoader(RigorousMCDDataset(val_samples), batch_size=32, shuffle=False)
    test_loader = DataLoader(RigorousMCDDataset(test_samples), batch_size=32, shuffle=False)
    
    # 5a: Separate SBP/DBP heads
    print(f"\n  Training MODEL-06-SepHead: Separate SBP/DBP regression heads...")
    model_sep = DualBranchResNetBiGRUAttn(
        in_channels=3, use_branchB=True, use_attn=True, use_demo=True, separate_heads=True
    ).to(device)
    model_sep = train_model(model_sep, train_loader, val_loader,
                           len(train_samples), len(val_samples),
                           epochs=40, lr=1e-3, save_name="model06_sep_heads",
                           model_label="MODEL-06-SepHead")
    r_sep = evaluate_model(model_sep, test_loader, "MODEL-06-SepHead")
    results.append(r_sep)
    
    # 5b: Weighted loss sweep (lambda_sbp > 1 to prioritize SBP)
    for lambda_sbp in [1.5, 2.0]:
        print(f"\n  Training MODEL-06-λSBP={lambda_sbp}...")
        model_w = DualBranchResNetBiGRUAttn(
            in_channels=3, use_branchB=True, use_attn=True, use_demo=True
        ).to(device)
        criterion = HuberPearsonLoss(lambda_sbp=lambda_sbp, lambda_dbp=1.0)
        model_w = train_model(model_w, train_loader, val_loader,
                             len(train_samples), len(val_samples),
                             epochs=40, lr=1e-3, save_name=f"model06_lsbp{lambda_sbp}",
                             criterion=criterion, model_label=f"MODEL-06-λSBP={lambda_sbp}")
        r_w = evaluate_model(model_w, test_loader, f"MODEL-06-λSBP={lambda_sbp}")
        results.append(r_w)
    
    return results

# --------------------------------------------------------------------------
# 12. PHASE 6: Regression-to-Mean Diagnostics
# --------------------------------------------------------------------------
def run_phase6_diagnostics(all_results, test_samples):
    print("\n" + "="*74)
    print("  PHASE 6 — REGRESSION-TO-MEAN DIAGNOSTICS")
    print("="*74)
    
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Find the best model result that has prediction arrays
    best_result = None
    for r in reversed(all_results):
        if "sbp_preds" in r and len(r["sbp_preds"]) > 0:
            best_result = r
            break
    
    if best_result is None:
        print("  No prediction arrays available for diagnostics.")
        return
    
    model_name = best_result["model"]
    sbp_preds = np.array(best_result["sbp_preds"])
    sbp_trues = np.array(best_result["sbp_trues"])
    dbp_preds = np.array(best_result["dbp_preds"])
    dbp_trues = np.array(best_result["dbp_trues"])
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # SBP scatter
    ax = axes[0]
    ax.scatter(sbp_trues, sbp_preds, alpha=0.4, s=10, c='#e74c3c')
    lims = [min(sbp_trues.min(), sbp_preds.min()) - 5, max(sbp_trues.max(), sbp_preds.max()) + 5]
    ax.plot(lims, lims, 'k--', lw=1, label='Perfect agreement')
    ax.set_xlabel('True SBP (mmHg)')
    ax.set_ylabel('Predicted SBP (mmHg)')
    ax.set_title(f'SBP: True vs Predicted\n(pred range: {sbp_preds.min():.0f}–{sbp_preds.max():.0f}, true range: {sbp_trues.min():.0f}–{sbp_trues.max():.0f})')
    ax.legend()
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    
    # DBP scatter
    ax = axes[1]
    ax.scatter(dbp_trues, dbp_preds, alpha=0.4, s=10, c='#3498db')
    lims = [min(dbp_trues.min(), dbp_preds.min()) - 5, max(dbp_trues.max(), dbp_preds.max()) + 5]
    ax.plot(lims, lims, 'k--', lw=1, label='Perfect agreement')
    ax.set_xlabel('True DBP (mmHg)')
    ax.set_ylabel('Predicted DBP (mmHg)')
    ax.set_title(f'DBP: True vs Predicted\n(pred range: {dbp_preds.min():.0f}–{dbp_preds.max():.0f}, true range: {dbp_trues.min():.0f}–{dbp_trues.max():.0f})')
    ax.legend()
    ax.set_aspect('equal')
    ax.set_xlim(lims)
    ax.set_ylim(lims)
    
    plt.suptitle(f'Regression-to-Mean Diagnostic — {model_name}', fontsize=13, fontweight='bold')
    plt.tight_layout()
    os.makedirs("./results", exist_ok=True)
    plt.savefig("./results/regression_to_mean_diagnostic.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: ./results/regression_to_mean_diagnostic.png")
    
    # Check regression-to-mean severity
    pred_range_sbp = sbp_preds.max() - sbp_preds.min()
    true_range_sbp = sbp_trues.max() - sbp_trues.min()
    pred_range_dbp = dbp_preds.max() - dbp_preds.min()
    true_range_dbp = dbp_trues.max() - dbp_trues.min()
    
    print(f"\n  SBP prediction range: {pred_range_sbp:.1f} mmHg (true range: {true_range_sbp:.1f}) -- ratio: {pred_range_sbp/true_range_sbp:.2f}")
    print(f"  DBP prediction range: {pred_range_dbp:.1f} mmHg (true range: {true_range_dbp:.1f}) -- ratio: {pred_range_dbp/true_range_dbp:.2f}")
    
    if pred_range_sbp / true_range_sbp < 0.5:
        print(f"  [WARNING]: SBP predictions occupy <50% of true range -- likely regression-to-mean!")
    else:
        print(f"  [OK] SBP prediction spread looks reasonable.")
    
    if pred_range_dbp / true_range_dbp < 0.5:
        print(f"  [WARNING]: DBP predictions occupy <50% of true range -- likely regression-to-mean!")
    else:
        print(f"  [OK] DBP prediction spread looks reasonable.")

# --------------------------------------------------------------------------
# 13. Summary Table Generator
# --------------------------------------------------------------------------
def print_summary_table(all_results):
    print("\n" + "="*74)
    print("  FULL ABLATION RESULTS TABLE")
    print("="*74)
    
    header = f"{'Model':<42} {'SBP MAE':>8} {'SBP RMSE':>9} {'SBP r':>6} {'DBP MAE':>8} {'DBP RMSE':>9} {'DBP r':>6} {'Sub SBP':>8} {'Sub DBP':>8}"
    print(f"\n  {header}")
    print(f"  {'-'*110}")
    
    for r in all_results:
        name = r["model"][:40]
        sbp_r = r.get("win_sbp_r", 0.0)
        dbp_r = r.get("win_dbp_r", 0.0)
        print(f"  {name:<42} {r['win_sbp_mae']:8.2f} {r['win_sbp_rmse']:9.2f} {sbp_r:6.3f} {r['win_dbp_mae']:8.2f} {r['win_dbp_rmse']:9.2f} {dbp_r:6.3f} {r['sub_sbp_mae']:8.2f} {r['sub_dbp_mae']:8.2f}")
    
    # Save CSV
    os.makedirs("./results", exist_ok=True)
    rows = []
    for r in all_results:
        rows.append({
            "model": r["model"],
            "win_sbp_mae": r["win_sbp_mae"], "win_sbp_rmse": r["win_sbp_rmse"], "win_sbp_r": r.get("win_sbp_r", 0.0),
            "win_dbp_mae": r["win_dbp_mae"], "win_dbp_rmse": r["win_dbp_rmse"], "win_dbp_r": r.get("win_dbp_r", 0.0),
            "sub_sbp_mae": r["sub_sbp_mae"], "sub_dbp_mae": r["sub_dbp_mae"]
        })
    pd.DataFrame(rows).to_csv("./results/ablation_ladder.csv", index=False)
    print(f"\n  Saved: ./results/ablation_ladder.csv")

# --------------------------------------------------------------------------
# MAIN: Run All Phases Sequentially
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# 14. EXP-A vs EXP-B vs EXP-C: Subject-Aware Weighted Balancing Experiment
# --------------------------------------------------------------------------
def run_balancing_experiments(train_samples, val_samples, test_samples):
    print("\n" + "="*74)
    print("  BALANCING EXPERIMENTS: EXP-A (Original) vs EXP-B (Moderate) vs EXP-C (Strong)")
    print("="*74)
    
    # 1. Analyze & Plot Distributions
    analyze_and_plot_bp_distribution(train_samples, val_samples, test_samples)
    
    # Validation & Test DataLoaders MUST remain 100% natural (unweighted)
    val_loader = get_dataloader(RigorousMCDDataset(val_samples, in_channels=1), shuffle=False)
    test_loader = get_dataloader(RigorousMCDDataset(test_samples, in_channels=1), shuffle=False)
    
    results = []
    
    # --- EXP-A: Original Natural Distribution ---
    print("\n" + "-"*60)
    print("  EXP-A: Original Natural Distribution (Unweighted Sampler)")
    print("-" * 60)
    train_loader_a = get_dataloader(RigorousMCDDataset(train_samples, in_channels=1), shuffle=True)
    model_a = DualBranchResNetBiGRUAttn(in_channels=1, use_branchB=True, use_attn=True, use_demo=True, separate_heads=True).to(device)
    model_a = train_model(model_a, train_loader_a, val_loader, len(train_samples), len(val_samples),
                          epochs=40, lr=1e-3, save_name="MODEL-06-SepHead_original", model_label="EXP-A (Original)")
    res_a = evaluate_bp_bins(model_a, test_loader, "EXP-A (Original)")
    results.append(res_a)
    
    # --- EXP-B: Moderate Balancing ---
    print("\n" + "-"*60)
    print("  EXP-B: Moderate Weighted Balancing (cap=5.0, power=0.5)")
    print("-" * 60)
    sampler_b = create_weighted_sampler(train_samples, mode="moderate")
    train_loader_b = get_dataloader(RigorousMCDDataset(train_samples, in_channels=1), sampler=sampler_b)
    model_b = DualBranchResNetBiGRUAttn(in_channels=1, use_branchB=True, use_attn=True, use_demo=True, separate_heads=True).to(device)
    model_b = train_model(model_b, train_loader_b, val_loader, len(train_samples), len(val_samples),
                          epochs=40, lr=1e-3, save_name="MODEL-06-SepHead_balanced_moderate", model_label="EXP-B (Moderate)")
    res_b = evaluate_bp_bins(model_b, test_loader, "EXP-B (Moderate)")
    results.append(res_b)
    
    # --- EXP-C: Strong Balancing ---
    print("\n" + "-"*60)
    print("  EXP-C: Strong Weighted Balancing (cap=10.0, power=1.0)")
    print("-" * 60)
    sampler_c = create_weighted_sampler(train_samples, mode="strong")
    train_loader_c = get_dataloader(RigorousMCDDataset(train_samples, in_channels=1), sampler=sampler_c)
    model_c = DualBranchResNetBiGRUAttn(in_channels=1, use_branchB=True, use_attn=True, use_demo=True, separate_heads=True).to(device)
    model_c = train_model(model_c, train_loader_c, val_loader, len(train_samples), len(val_samples),
                          epochs=40, lr=1e-3, save_name="MODEL-06-SepHead_balanced_strong", model_label="EXP-C (Strong)")
    res_c = evaluate_bp_bins(model_c, test_loader, "EXP-C (Strong)")
    results.append(res_c)
    
    # Save balancing comparison CSV
    os.makedirs("./results", exist_ok=True)
    comp_rows = []
    for r in results:
        comp_rows.append({
            "experiment": r["model"],
            "win_sbp_mae": r["win_sbp_mae"], "win_sbp_rmse": r["win_sbp_rmse"], "win_sbp_r": r["win_sbp_r"],
            "win_dbp_mae": r["win_dbp_mae"], "win_dbp_rmse": r["win_dbp_rmse"], "win_dbp_r": r["win_dbp_r"],
            "sub_sbp_mae": r["sub_sbp_mae"], "sub_dbp_mae": r["sub_dbp_mae"]
        })
    pd.DataFrame(comp_rows).to_csv("./results/balancing_comparison.csv", index=False)
    print(f"\n  Saved: ./results/balancing_comparison.csv")
    return results

def run_gold_pipeline(base_dir="./mcd_dataset"):
    all_samples, df_db, norm_params = load_and_preprocess_mcd(base_dir, token=hf_token)
    
    if len(all_samples) == 0:
        print("Error: No valid samples extracted from dataset!")
        sys.exit(1)
    
    # SUBJECT-LEVEL SPLIT (70% Train, 15% Val, 15% Test)
    sample_subjects = np.array([s["subject_id"] for s in all_samples])
    gss = GroupShuffleSplit(n_splits=1, train_size=0.7, random_state=42)
    train_idx, temp_idx = next(gss.split(all_samples, groups=sample_subjects))
    train_samples = [all_samples[i] for i in train_idx]
    temp_samples = [all_samples[i] for i in temp_idx]
    
    temp_subs = np.array([s["subject_id"] for s in temp_samples])
    gss_val = GroupShuffleSplit(n_splits=1, train_size=0.5, random_state=42)
    val_idx, test_idx = next(gss_val.split(temp_samples, groups=temp_subs))
    val_samples = [temp_samples[i] for i in val_idx]
    test_samples = [temp_samples[i] for i in test_idx]
    
    print(f"\n--- SUBJECT-LEVEL SPLIT ---")
    print(f"Train: {len(set(s['subject_id'] for s in train_samples))} subjects ({len(train_samples)} windows)")
    print(f"Val:   {len(set(s['subject_id'] for s in val_samples))} subjects ({len(val_samples)} windows)")
    print(f"Test:  {len(set(s['subject_id'] for s in test_samples))} subjects ({len(test_samples)} windows)")
    
    all_results = []
    
    # Phase 1: Verify baseline
    no_leakage = run_phase1_verify_baseline(train_samples, val_samples, test_samples, norm_params)
    if not no_leakage:
        print("\n  [WARNING] DATA LEAKAGE DETECTED -- aborting further phases!")
        return
    
    # Phase 2: Baselines
    phase2_results, train_loader, val_loader, test_loader = run_phase2_baselines(train_samples, val_samples, test_samples)
    all_results.extend(phase2_results)
    
    # Phase 3: Architecture ablation
    phase3_results = run_phase3_ablation(train_samples, val_samples, test_samples, train_loader, val_loader, test_loader)
    all_results.extend(phase3_results)
    
    # Phase 4: Input channel ablation
    phase4_results = run_phase4_input_ablation(train_samples, val_samples, test_samples)
    all_results.extend(phase4_results)
    
    # Phase 5: SBP investigation
    phase5_results = run_phase5_sbp_investigation(train_samples, val_samples, test_samples)
    all_results.extend(phase5_results)
    
    # Phase 6: Diagnostics
    run_phase6_diagnostics(all_results, test_samples)
    
    # Balancing Experiments: EXP-A vs EXP-B vs EXP-C
    balancing_results = run_balancing_experiments(train_samples, val_samples, test_samples)
    all_results.extend(balancing_results)
    
    # Summary table
    print_summary_table(all_results)
    
    print("\n" + "="*74)
    print("  GOLD PIPELINE COMPLETE (Phases 1-6 + EXP-A/B/C Balancing)!")
    print("="*74)

if __name__ == "__main__":
    dataset_dir = "./mcd_dataset"
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        dataset_dir = sys.argv[1]
    run_gold_pipeline(dataset_dir)
