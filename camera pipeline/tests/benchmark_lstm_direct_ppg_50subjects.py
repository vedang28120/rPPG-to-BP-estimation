import os
import sys

# Setup environment for legacy Keras & protobuf
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import types
dummy = types.ModuleType('runtime_version')
dummy.Domain = type('Domain', (), {'PUBLIC': 1})
dummy.ValidateProtobufRuntimeVersion = lambda *args, **kwargs: None
sys.modules['google.protobuf.runtime_version'] = dummy
import google.protobuf
google.protobuf.runtime_version = dummy

import numpy as np
import pandas as pd
import tf_keras
import matplotlib.pyplot as plt
from huggingface_hub import hf_hub_download

# Pipeline test output directory
current_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_dir = os.path.dirname(current_dir)
test_out_dir = os.path.join(pipeline_dir, "tests")
os.makedirs(test_out_dir, exist_ok=True)

print("==========================================================================")
print("       DIRECT LSTM MODEL BENCHMARK ON CONTACT PPG DATA (50 SUBJECTS)       ")
print("==========================================================================")

# 1. Load db.csv metadata
print("Loading MCD dataset metadata (db.csv)...")
db_csv_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset')
df_db = pd.read_csv(db_csv_path)

# Filter for unique patient trials with valid upper_ap (SBP) and lower_ap (DBP)
df_valid = df_db[(df_db['upper_ap'].notnull()) & (df_db['lower_ap'].notnull())].drop_duplicates(subset=['patient_id', 'step']).copy()
print(f"Total available subject trials in db.csv: {len(df_valid)}")

# 2. Load LSTM Model
model_path = os.path.join(pipeline_dir, "..", "project prototype", "models", "lstm_ppg_nonmixed.h5")
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    sys.exit(1)

print(f"Loading LSTM Model: {model_path}...")
model = tf_keras.models.load_model(model_path, compile=False)
print("Model loaded successfully.\n")

mcd_base_dir = r"E:\VT\PPG rPPG BP project\MCD_rppg"

results = []
target_trials = 50
processed = 0

for idx, row in df_valid.iterrows():
    if processed >= target_trials:
        break
        
    pid = int(row['patient_id'])
    step = str(row['step'])  # 'before' or 'after'
    
    # Path to contact PPG (.PW or ppg_sync .txt file)
    sub_dir = os.path.join(mcd_base_dir, f"Subject_{pid}")
    pw_path = os.path.join(sub_dir, "ppg", "ppg", f"{pid}_{step}.PW")
    if not os.path.exists(pw_path):
        pw_path = os.path.join(sub_dir, "ppg", f"{pid}_{step}.PW")
        
    sync_path = os.path.join(sub_dir, "ppg_sync", "ppg_sync", f"{pid}_IriunWebcam_{step}.txt")
    if not os.path.exists(sync_path):
        sync_path = os.path.join(sub_dir, "ppg_sync", f"{pid}_IriunWebcam_{step}.txt")
        
    ppg_raw_signal = []
    
    # Try reading .PW ground truth first
    if os.path.exists(pw_path):
        with open(pw_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    try: ppg_raw_signal.append(float(parts[0]))
                    except: pass
    elif os.path.exists(sync_path):
        with open(sync_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 1:
                    try: ppg_raw_signal.append(float(parts[0]))
                    except: pass
                    
    if len(ppg_raw_signal) < 875:
        continue
        
    # Take 875-point segment (7 seconds @ 125 Hz)
    ppg_window = np.array(ppg_raw_signal[:875])
    
    # Apply Z-score normalization: (x - mean) / std
    std_val = np.std(ppg_window)
    if std_val == 0: std_val = 1e-8
    norm_ppg = (ppg_window - np.mean(ppg_window)) / std_val
    
    # Model inference
    preds = model.predict(norm_ppg.reshape(1, 875, 1), verbose=0)
    p1 = float(preds[0][0][0])
    p2 = float(preds[1][0][0])
    
    sbp_pred = max(p1, p2)
    dbp_pred = min(p1, p2)
    
    actual_sbp = float(row['upper_ap'])
    actual_dbp = float(row['lower_ap'])
    actual_hr = float(row['pulse']) if not np.isnan(row['pulse']) else 0.0
    actual_map = actual_dbp + (actual_sbp - actual_dbp) / 3.0
    pred_map = dbp_pred + (sbp_pred - dbp_pred) / 3.0
    
    sbp_err = abs(sbp_pred - actual_sbp)
    dbp_err = abs(dbp_pred - actual_dbp)
    
    results.append({
        "subject_id": pid,
        "step": step,
        "actual_sbp": actual_sbp,
        "pred_sbp": round(sbp_pred, 1),
        "sbp_err": round(sbp_err, 1),
        "actual_dbp": actual_dbp,
        "pred_dbp": round(dbp_pred, 1),
        "dbp_err": round(dbp_err, 1),
        "actual_map": round(actual_map, 1),
        "pred_map": round(pred_map, 1),
        "actual_hr": actual_hr
    })
    
    processed += 1
    print(f"[{processed}/{target_trials}] Subject {pid} ({step}): Actual SBP={actual_sbp}, Pred SBP={sbp_pred:.1f} (Err: {sbp_err:.1f}) | Actual DBP={actual_dbp}, Pred DBP={dbp_pred:.1f} (Err: {dbp_err:.1f})", flush=True)

# 3. Compute Summary Performance Metrics
df_res = pd.DataFrame(results)
csv_path = os.path.join(test_out_dir, "lstm_direct_ppg_50subjects.csv")
df_res.to_csv(csv_path, index=False)

mae_sbp = np.mean(df_res['sbp_err'])
rmse_sbp = np.sqrt(np.mean((df_res['pred_sbp'] - df_res['actual_sbp'])**2))
r_sbp = np.corrcoef(df_res['actual_sbp'], df_res['pred_sbp'])[0, 1] if len(df_res) > 1 else 0.0

mae_dbp = np.mean(df_res['dbp_err'])
rmse_dbp = np.sqrt(np.mean((df_res['pred_dbp'] - df_res['actual_dbp'])**2))
r_dbp = np.corrcoef(df_res['actual_dbp'], df_res['pred_dbp'])[0, 1] if len(df_res) > 1 else 0.0

# 4. Generate Markdown Report
md_report_path = os.path.join(test_out_dir, "accuracy_report_lstm_direct_ppg.md")
with open(md_report_path, "w", encoding="utf-8") as f:
    f.write("# Standalone LSTM Model Benchmark on Contact PPG Signals (50 Subjects)\n\n")
    f.write(f"Evaluated the LSTM Blood Pressure model **directly on raw contact PPG sensor signals** (`.PW`) across **{len(df_res)} MCD dataset trials**, isolating model performance from camera/rPPG video extraction noise.\n\n")
    f.write("### 📊 Direct LSTM Model Accuracy Metrics\n\n")
    f.write("| Vital Metric | MAE (Mean Abs Error) | RMSE (Root Mean Sq Error) | Pearson Correlation (r) |\n")
    f.write("|---|---|---|---|\n")
    f.write(f"| **Systolic BP (SBP)** | **`{mae_sbp:.2f} mmHg`** | `{rmse_sbp:.2f} mmHg` | `{r_sbp:.3f}` |\n")
    f.write(f"| **Diastolic BP (DBP)** | **`{mae_dbp:.2f} mmHg`** | `{rmse_dbp:.2f} mmHg` | `{r_dbp:.3f}` |\n\n")
    
    f.write("### 📋 Subject-by-Subject Prediction Breakdown\n\n")
    f.write("| Subject ID | Trial | Actual SBP | Pred SBP | SBP Err | Actual DBP | Pred DBP | DBP Err | Actual MAP | Pred MAP |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for r in results:
        f.write(f"| {r['subject_id']} | {r['step']} | {r['actual_sbp']} | {r['pred_sbp']} | {r['sbp_err']} | {r['actual_dbp']} | {r['pred_dbp']} | {r['dbp_err']} | {r['actual_map']} | {r['pred_map']} |\n")

# 5. Generate Scatter & Bland-Altman Plots
fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# SBP Scatter
axes[0, 0].scatter(df_res['actual_sbp'], df_res['pred_sbp'], alpha=0.7, color='#E91E63', edgecolors='k')
axes[0, 0].plot([80, 160], [80, 160], 'r--', label='Ideal 1:1')
axes[0, 0].set_xlabel('Actual Systolic BP (mmHg)')
axes[0, 0].set_ylabel('Predicted Systolic BP (mmHg)')
axes[0, 0].set_title(f'Direct PPG SBP: Actual vs Predicted (MAE={mae_sbp:.2f} mmHg)')
axes[0, 0].legend()
axes[0, 0].grid(True, linestyle='--', alpha=0.5)

# DBP Scatter
axes[0, 1].scatter(df_res['actual_dbp'], df_res['pred_dbp'], alpha=0.7, color='#00BCD4', edgecolors='k')
axes[0, 1].plot([50, 110], [50, 110], 'r--', label='Ideal 1:1')
axes[0, 1].set_xlabel('Actual Diastolic BP (mmHg)')
axes[0, 1].set_ylabel('Predicted Diastolic BP (mmHg)')
axes[0, 1].set_title(f'Direct PPG DBP: Actual vs Predicted (MAE={mae_dbp:.2f} mmHg)')
axes[0, 1].legend()
axes[0, 1].grid(True, linestyle='--', alpha=0.5)

# Bland-Altman SBP
mean_sbp = (df_res['actual_sbp'] + df_res['pred_sbp']) / 2.0
diff_sbp = df_res['pred_sbp'] - df_res['actual_sbp']
md_sbp = np.mean(diff_sbp)
sd_sbp = np.std(diff_sbp)

axes[1, 0].scatter(mean_sbp, diff_sbp, alpha=0.7, color='#9C27B0', edgecolors='k')
axes[1, 0].axhline(md_sbp, color='blue', linestyle='-', label=f'Mean Bias ({md_sbp:+.1f})')
axes[1, 0].axhline(md_sbp + 1.96*sd_sbp, color='red', linestyle='--', label=f'+1.96 SD ({md_sbp+1.96*sd_sbp:+.1f})')
axes[1, 0].axhline(md_sbp - 1.96*sd_sbp, color='red', linestyle='--', label=f'-1.96 SD ({md_sbp-1.96*sd_sbp:+.1f})')
axes[1, 0].set_xlabel('Mean SBP (mmHg)')
axes[1, 0].set_ylabel('Difference (Pred - Actual mmHg)')
axes[1, 0].set_title('Bland-Altman Plot: Direct PPG SBP')
axes[1, 0].legend()
axes[1, 0].grid(True, linestyle='--', alpha=0.5)

# Bland-Altman DBP
mean_dbp = (df_res['actual_dbp'] + df_res['pred_dbp']) / 2.0
diff_dbp = df_res['pred_dbp'] - df_res['actual_dbp']
md_dbp = np.mean(diff_dbp)
sd_dbp = np.std(diff_dbp)

axes[1, 1].scatter(mean_dbp, diff_dbp, alpha=0.7, color='#4CAF50', edgecolors='k')
axes[1, 1].axhline(md_dbp, color='blue', linestyle='-', label=f'Mean Bias ({md_dbp:+.1f})')
axes[1, 1].axhline(md_dbp + 1.96*sd_dbp, color='red', linestyle='--', label=f'+1.96 SD ({md_dbp+1.96*sd_dbp:+.1f})')
axes[1, 1].axhline(md_dbp - 1.96*sd_dbp, color='red', linestyle='--', label=f'-1.96 SD ({md_dbp-1.96*sd_dbp:+.1f})')
axes[1, 1].set_xlabel('Mean DBP (mmHg)')
axes[1, 1].set_ylabel('Difference (Pred - Actual mmHg)')
axes[1, 1].set_title('Bland-Altman Plot: Direct PPG DBP')
axes[1, 1].legend()
axes[1, 1].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plot_path = os.path.join(test_out_dir, "bland_altman_lstm_direct_ppg.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"\n==========================================================================")
print(f"Direct Contact PPG Benchmark Complete ({len(df_res)} subjects)!")
print(f"  - SBP MAE: {mae_sbp:.2f} mmHg (RMSE: {rmse_sbp:.2f}, r={r_sbp:.3f})")
print(f"  - DBP MAE: {mae_dbp:.2f} mmHg (RMSE: {rmse_dbp:.2f}, r={r_dbp:.3f})")
print(f"Outputs saved to:\n  - CSV: {csv_path}\n  - Report: {md_report_path}\n  - Plots: {plot_path}")
print(f"==========================================================================")
