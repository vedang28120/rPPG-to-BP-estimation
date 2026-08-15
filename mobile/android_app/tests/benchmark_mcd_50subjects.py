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

import cv2
import numpy as np
import pandas as pd
import scipy.signal as signal
import tf_keras
import matplotlib.pyplot as plt
from huggingface_hub import hf_hub_download

# Add python source path
current_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(pipeline_dir, "app", "src", "main", "python"))

import pos_engine

# Output test directory
test_out_dir = os.path.join(pipeline_dir, "tests")
os.makedirs(test_out_dir, exist_ok=True)

print("==========================================================================")
print("              MCD DATASET 50-SUBJECT PIPELINE BENCHMARK                  ")
print("==========================================================================")

# 1. Download/Load db.csv from HuggingFace
print("Loading MCD dataset database metadata (db.csv)...")
db_csv_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset')
df_db = pd.read_csv(db_csv_path)

# Filter for IriunWebcam entries with valid SBP (upper_ap) and DBP (lower_ap)
df_iriun = df_db[(df_db['camera'] == 'IriunWebcam') & (df_db['upper_ap'].notnull()) & (df_db['lower_ap'].notnull())].copy()
print(f"Total valid IriunWebcam entries in db.csv: {len(df_iriun)}")

# 2. Load Blood Pressure Model
model_path = os.path.join(pipeline_dir, "..", "project prototype", "models", "lstm_ppg_nonmixed.h5")
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    sys.exit(1)

print(f"Loading Blood Pressure Model: {model_path}...")
model = tf_keras.models.load_model(model_path, compile=False)
print("Model loaded successfully.\n")

mcd_base_dir = r"E:\VT\PPG rPPG BP project\MCD_rppg"

def extract_rgb_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None, None
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps): fps = 30.0
    
    rgb_frames = []
    timestamps = []
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape
        
        # Forehead & Cheek ROIs
        fh_roi = frame_rgb[int(h * 0.15):int(h * 0.35), int(w * 0.35):int(w * 0.65)]
        lc_roi = frame_rgb[int(h * 0.45):int(h * 0.65), int(w * 0.20):int(w * 0.40)]
        rc_roi = frame_rgb[int(h * 0.45):int(h * 0.65), int(w * 0.60):int(w * 0.80)]
        
        fh_rgb = np.mean(fh_roi, axis=(0, 1)) if fh_roi.size > 0 else np.array([128.0, 128.0, 128.0])
        lc_rgb = np.mean(lc_roi, axis=(0, 1)) if lc_roi.size > 0 else np.array([128.0, 128.0, 128.0])
        rc_rgb = np.mean(rc_roi, axis=(0, 1)) if rc_roi.size > 0 else np.array([128.0, 128.0, 128.0])
        
        frame_data = np.concatenate([fh_rgb, fh_rgb, fh_rgb, lc_rgb, rc_rgb])
        rgb_frames.append(frame_data)
        timestamps.append(frame_idx * (1000.0 / fps))
        frame_idx += 1
        
    cap.release()
    return np.array(rgb_frames), np.array(timestamps)

results = []
target_count = 50
processed = 0

for idx, row in df_iriun.iterrows():
    if processed >= target_count:
        break
        
    pid = int(row['patient_id'])
    step = str(row['step']) # 'before' or 'after'
    
    # Expected video path in MCD_rppg structure
    video_filename = f"{pid}_IriunWebcam_{step}.avi"
    video_path = os.path.join(mcd_base_dir, f"Subject_{pid}", "video", "video", video_filename)
    if not os.path.exists(video_path):
        video_path = os.path.join(mcd_base_dir, f"Subject_{pid}", "video", video_filename)
        
    if not os.path.exists(video_path):
        continue
        
    actual_sbp = float(row['upper_ap'])
    actual_dbp = float(row['lower_ap'])
    actual_hr = float(row['pulse']) if not np.isnan(row['pulse']) else 0.0
    actual_map = actual_dbp + (actual_sbp - actual_dbp) / 3.0
    
    rgb_data, timestamps = extract_rgb_from_video(video_path)
    if rgb_data is None or len(rgb_data) < 210:
        continue
        
    rgb_window = rgb_data[:210]
    ts_window = timestamps[:210]
    
    status, multi_tensor, hr_pred, hrv_pred, rr_pred = pos_engine.process_window(
        rgb_window.flatten(), ts_window, None, "RECORDING"
    )
    
    if status != "SUCCESS":
        continue
        
    tensor_arr = np.array(multi_tensor) # [875, 3]
    ppg_signal = tensor_arr[:, 0].reshape(1, 875, 1)
    
    preds = model.predict(ppg_signal, verbose=0)
    p1 = float(preds[0][0][0])
    p2 = float(preds[1][0][0])
    
    sbp_pred = max(p1, p2)
    dbp_pred = min(p1, p2)
    map_pred = dbp_pred + (sbp_pred - dbp_pred) / 3.0
    
    sbp_err = abs(sbp_pred - actual_sbp)
    dbp_err = abs(dbp_pred - actual_dbp)
    hr_err = abs(hr_pred - actual_hr) if actual_hr > 0 else 0.0
    
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
        "pred_map": round(map_pred, 1),
        "actual_hr": actual_hr,
        "pred_hr": round(hr_pred, 1),
        "hr_err": round(hr_err, 1)
    })
    
    processed += 1
    print(f"[{processed}/{target_count}] Subject {pid} ({step}): Actual SBP={actual_sbp}, Pred SBP={sbp_pred:.1f} | Actual DBP={actual_dbp}, Pred DBP={dbp_pred:.1f}", flush=True)

df_res = pd.DataFrame(results)
csv_path = os.path.join(test_out_dir, "mcd_50subjects_benchmark.csv")
df_res.to_csv(csv_path, index=False)

# Compute Statistical Performance Metrics
mae_sbp = np.mean(df_res['sbp_err'])
rmse_sbp = np.sqrt(np.mean((df_res['pred_sbp'] - df_res['actual_sbp'])**2))
r_sbp = np.corrcoef(df_res['actual_sbp'], df_res['pred_sbp'])[0, 1] if len(df_res) > 1 else 0.0

mae_dbp = np.mean(df_res['dbp_err'])
rmse_dbp = np.sqrt(np.mean((df_res['pred_dbp'] - df_res['actual_dbp'])**2))
r_dbp = np.corrcoef(df_res['actual_dbp'], df_res['pred_dbp'])[0, 1] if len(df_res) > 1 else 0.0

valid_hr_df = df_res[df_res['actual_hr'] > 0]
mae_hr = np.mean(valid_hr_df['hr_err']) if len(valid_hr_df) > 0 else 0.0

# Save Detailed Markdown Report
md_report_path = os.path.join(test_out_dir, "accuracy_report_50subjects.md")
with open(md_report_path, "w", encoding="utf-8") as f:
    f.write("# MCD Dataset 50-Subject Comprehensive Model Benchmark\n\n")
    f.write(f"Evaluated **{len(df_res)} subjects** from the MCD Dataset against true blood pressure measurements.\n\n")
    f.write("### 📊 Statistical Error Summary\n\n")
    f.write("| Metric | MAE (Mean Abs Error) | RMSE (Root Mean Sq Error) | Pearson Correlation (r) |\n")
    f.write("|---|---|---|---|\n")
    f.write(f"| **Systolic BP (SBP)** | **`{mae_sbp:.2f} mmHg`** | `{rmse_sbp:.2f} mmHg` | `{r_sbp:.3f}` |\n")
    f.write(f"| **Diastolic BP (DBP)** | **`{mae_dbp:.2f} mmHg`** | `{rmse_dbp:.2f} mmHg` | `{r_dbp:.3f}` |\n")
    f.write(f"| **Heart Rate (HR)** | **`{mae_hr:.2f} BPM`** | - | - |\n\n")
    
    f.write("### 📋 Subject-by-Subject Prediction Breakdown\n\n")
    f.write("| Subject ID | Trial | Actual SBP | Pred SBP | SBP Err | Actual DBP | Pred DBP | DBP Err | Actual MAP | Pred MAP |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for r in results:
        f.write(f"| {r['subject_id']} | {r['step']} | {r['actual_sbp']} | {r['pred_sbp']} | {r['sbp_err']} | {r['actual_dbp']} | {r['pred_dbp']} | {r['dbp_err']} | {r['actual_map']} | {r['pred_map']} |\n")

# Generate Scatter & Bland-Altman Plots
fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# SBP Scatter
axes[0, 0].scatter(df_res['actual_sbp'], df_res['pred_sbp'], alpha=0.7, color='#9C27B0', edgecolors='k')
axes[0, 0].plot([80, 160], [80, 160], 'r--', label='Ideal 1:1')
axes[0, 0].set_xlabel('Actual Systolic BP (mmHg)')
axes[0, 0].set_ylabel('Predicted Systolic BP (mmHg)')
axes[0, 0].set_title(f'SBP Prediction vs Actual (MAE={mae_sbp:.2f} mmHg)')
axes[0, 0].legend()
axes[0, 0].grid(True, linestyle='--', alpha=0.5)

# DBP Scatter
axes[0, 1].scatter(df_res['actual_dbp'], df_res['pred_dbp'], alpha=0.7, color='#2196F3', edgecolors='k')
axes[0, 1].plot([50, 110], [50, 110], 'r--', label='Ideal 1:1')
axes[0, 1].set_xlabel('Actual Diastolic BP (mmHg)')
axes[0, 1].set_ylabel('Predicted Diastolic BP (mmHg)')
axes[0, 1].set_title(f'DBP Prediction vs Actual (MAE={mae_dbp:.2f} mmHg)')
axes[0, 1].legend()
axes[0, 1].grid(True, linestyle='--', alpha=0.5)

# Bland-Altman SBP
mean_sbp = (df_res['actual_sbp'] + df_res['pred_sbp']) / 2.0
diff_sbp = df_res['pred_sbp'] - df_res['actual_sbp']
md_sbp = np.mean(diff_sbp)
sd_sbp = np.std(diff_sbp)

axes[1, 0].scatter(mean_sbp, diff_sbp, alpha=0.7, color='#E91E63', edgecolors='k')
axes[1, 0].axhline(md_sbp, color='blue', linestyle='-', label=f'Mean Bias ({md_sbp:+.1f})')
axes[1, 0].axhline(md_sbp + 1.96*sd_sbp, color='red', linestyle='--', label=f'+1.96 SD ({md_sbp+1.96*sd_sbp:+.1f})')
axes[1, 0].axhline(md_sbp - 1.96*sd_sbp, color='red', linestyle='--', label=f'-1.96 SD ({md_sbp-1.96*sd_sbp:+.1f})')
axes[1, 0].set_xlabel('Mean SBP (mmHg)')
axes[1, 0].set_ylabel('Difference (Pred - Actual mmHg)')
axes[1, 0].set_title('Bland-Altman Plot: Systolic BP')
axes[1, 0].legend()
axes[1, 0].grid(True, linestyle='--', alpha=0.5)

# Bland-Altman DBP
mean_dbp = (df_res['actual_dbp'] + df_res['pred_dbp']) / 2.0
diff_dbp = df_res['pred_dbp'] - df_res['actual_dbp']
md_dbp = np.mean(diff_dbp)
sd_dbp = np.std(diff_dbp)

axes[1, 1].scatter(mean_dbp, diff_dbp, alpha=0.7, color='#009688', edgecolors='k')
axes[1, 1].axhline(md_dbp, color='blue', linestyle='-', label=f'Mean Bias ({md_dbp:+.1f})')
axes[1, 1].axhline(md_dbp + 1.96*sd_dbp, color='red', linestyle='--', label=f'+1.96 SD ({md_dbp+1.96*sd_dbp:+.1f})')
axes[1, 1].axhline(md_dbp - 1.96*sd_dbp, color='red', linestyle='--', label=f'-1.96 SD ({md_dbp-1.96*sd_dbp:+.1f})')
axes[1, 1].set_xlabel('Mean DBP (mmHg)')
axes[1, 1].set_ylabel('Difference (Pred - Actual mmHg)')
axes[1, 1].set_title('Bland-Altman Plot: Diastolic BP')
axes[1, 1].legend()
axes[1, 1].grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plot_path = os.path.join(test_out_dir, "bland_altman_50subjects.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"\n==========================================================================")
print(f"50-Subject Benchmark Complete!")
print(f"  - SBP MAE: {mae_sbp:.2f} mmHg (RMSE: {rmse_sbp:.2f})")
print(f"  - DBP MAE: {mae_dbp:.2f} mmHg (RMSE: {rmse_dbp:.2f})")
print(f"  - HR  MAE: {mae_hr:.2f} BPM")
print(f"Reports & Plots saved to:\n  - CSV: {csv_path}\n  - Markdown: {md_report_path}\n  - Plots: {plot_path}")
print(f"==========================================================================")
