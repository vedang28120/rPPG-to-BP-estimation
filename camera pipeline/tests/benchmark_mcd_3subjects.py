import os
import sys

# Setup compatibility environment for legacy Keras & protobuf
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

# Add python source path
current_dir = os.path.dirname(os.path.abspath(__file__))
pipeline_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(pipeline_dir, "app", "src", "main", "python"))

import pos_engine

# Output test directory
test_out_dir = os.path.join(pipeline_dir, "tests")
os.makedirs(test_out_dir, exist_ok=True)

# Ground truth values from MCD dataset db.csv for IriunWebcam_before recordings
ground_truth_db = {
    "Subject_1020": {
        "video": r"E:\VT\PPG rPPG BP project\MCD_rppg\Subject_1020\video\video\1020_IriunWebcam_before.avi",
        "sbp_actual": 105.0,
        "dbp_actual": 78.0,
        "hr_actual": 83.0,
        "age": 23,
        "gender": "F"
    },
    "Subject_1024": {
        "video": r"E:\VT\PPG rPPG BP project\MCD_rppg\Subject_1024\video\video\1024_IriunWebcam_before.avi",
        "sbp_actual": 106.0,
        "dbp_actual": 59.0,
        "hr_actual": 78.0,
        "age": 19,
        "gender": "F"
    },
    "Subject_1035": {
        "video": r"E:\VT\PPG rPPG BP project\MCD_rppg\Subject_1035\video\video\1035_IriunWebcam_before.avi",
        "sbp_actual": 112.0,
        "dbp_actual": 72.0,
        "hr_actual": 93.0,
        "age": 18,
        "gender": "M"
    }
}

print("==========================================================================")
print("              MCD DATASET PIPELINE BENCHMARK EVALUATION                  ")
print("==========================================================================")

# 1. Load BP Prediction LSTM Model
model_path = os.path.join(pipeline_dir, "..", "project prototype", "models", "lstm_ppg_nonmixed.h5")
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    sys.exit(1)

print(f"Loading Blood Pressure Model: {model_path}...")
model = tf_keras.models.load_model(model_path, compile=False)
print("Model loaded successfully.\n")

def extract_rgb_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return None, None
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps): fps = 30.0
    
    rgb_frames = []
    timestamps = []
    frame_idx = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame_rgb.shape
        
        # Forehead ROI (Top-center 20% to 50% height, 35% to 65% width)
        fh_roi = frame_rgb[int(h * 0.15):int(h * 0.35), int(w * 0.35):int(w * 0.65)]
        lc_roi = frame_rgb[int(h * 0.45):int(h * 0.65), int(w * 0.20):int(w * 0.40)]
        rc_roi = frame_rgb[int(h * 0.45):int(h * 0.65), int(w * 0.60):int(w * 0.80)]
        
        fh_rgb = np.mean(fh_roi, axis=(0, 1))
        lc_rgb = np.mean(lc_roi, axis=(0, 1))
        rc_rgb = np.mean(rc_roi, axis=(0, 1))
        
        # Stack into 15-channel array matching Android tracker output
        frame_data = np.concatenate([fh_rgb, fh_rgb, fh_rgb, lc_rgb, rc_rgb])
        rgb_frames.append(frame_data)
        timestamps.append(frame_idx * (1000.0 / fps))
        frame_idx += 1
        
    cap.release()
    return np.array(rgb_frames), np.array(timestamps)

results = []

for sub_name, info in ground_truth_db.items():
    print(f"Processing {sub_name} ({info['video']})...")
    
    rgb_data, timestamps = extract_rgb_from_video(info['video'])
    if rgb_data is None or len(rgb_data) < 210:
        print(f"Skipping {sub_name}: Insufficient video frames ({len(rgb_data) if rgb_data is not None else 0}).")
        continue
        
    # Take 7-second window (210 frames at 30fps)
    rgb_window = rgb_data[:210]
    ts_window = timestamps[:210]
    
    # Process through pipeline
    status, multi_tensor, hr_pred, hrv_pred, rr_pred = pos_engine.process_window(
        rgb_window.flatten(), ts_window, None, "RECORDING"
    )
    
    if status != "SUCCESS":
        print(f"  SQI Failed for {sub_name}: {status}")
        continue
        
    # Extract primary normalized PPG channel for LSTM model (875 points)
    tensor_arr = np.array(multi_tensor) # shape [875, 3]
    ppg_signal = tensor_arr[:, 0].reshape(1, 875, 1) # Primary PPG
    
    # Predict BP using model
    preds = model.predict(ppg_signal, verbose=0)
    p1 = float(preds[0][0][0])
    p2 = float(preds[1][0][0])
    
    sbp_pred = max(p1, p2)
    dbp_pred = min(p1, p2)
    
    map_actual = info['dbp_actual'] + (info['sbp_actual'] - info['dbp_actual']) / 3.0
    map_pred = dbp_pred + (sbp_pred - dbp_pred) / 3.0
    
    sbp_err = abs(sbp_pred - info['sbp_actual'])
    dbp_err = abs(dbp_pred - info['dbp_actual'])
    hr_err = abs(hr_pred - info['hr_actual'])
    
    results.append({
        "subject": sub_name,
        "hr_actual": info['hr_actual'],
        "hr_pred": round(hr_pred, 1),
        "hr_err": round(hr_err, 1),
        "sbp_actual": info['sbp_actual'],
        "sbp_pred": round(sbp_pred, 1),
        "sbp_err": round(sbp_err, 1),
        "dbp_actual": info['dbp_actual'],
        "dbp_pred": round(dbp_pred, 1),
        "dbp_err": round(dbp_err, 1),
        "map_actual": round(map_actual, 1),
        "map_pred": round(map_pred, 1),
        "hrv_pred": round(hrv_pred, 1)
    })
    
    print(f"  Actual  -> SBP: {info['sbp_actual']} mmHg | DBP: {info['dbp_actual']} mmHg | HR: {info['hr_actual']} BPM")
    print(f"  Predict -> SBP: {sbp_pred:.1f} mmHg | DBP: {dbp_pred:.1f} mmHg | HR: {hr_pred:.1f} BPM")
    print(f"  Errors  -> SBP: {sbp_err:.1f} | DBP: {dbp_err:.1f} | HR: {hr_err:.1f}\n")

# Save Results to CSV & Markdown
df_res = pd.DataFrame(results)
csv_path = os.path.join(test_out_dir, "mcd_accuracy_benchmark.csv")
df_res.to_csv(csv_path, index=False)

# Generate Markdown Report
md_report_path = os.path.join(test_out_dir, "accuracy_report.md")
with open(md_report_path, "w") as f:
    f.write("# MCD Dataset Model Accuracy Benchmark Report\n\n")
    f.write("Evaluation of current rPPG POS extraction engine & LSTM Blood Pressure Model against MCD dataset ground truths.\n\n")
    f.write("### Prediction vs Actual Ground Truth\n\n")
    f.write("| Subject | Actual HR | Pred HR | HR Err | Actual SBP | Pred SBP | SBP Err | Actual DBP | Pred DBP | DBP Err | Actual MAP | Pred MAP |\n")
    f.write("|---------|-----------|---------|--------|------------|----------|---------|------------|----------|---------|------------|----------|\n")
    for r in results:
        f.write(f"| {r['subject']} | {r['hr_actual']} | {r['hr_pred']} | {r['hr_err']} | {r['sbp_actual']} | {r['sbp_pred']} | {r['sbp_err']} | {r['dbp_actual']} | {r['dbp_pred']} | {r['dbp_err']} | {r['map_actual']} | {r['map_pred']} |\n")
    
    mean_sbp_err = np.mean([r['sbp_err'] for r in results])
    mean_dbp_err = np.mean([r['dbp_err'] for r in results])
    mean_hr_err = np.mean([r['hr_err'] for r in results])
    
    f.write(f"\n### Mean Absolute Errors (MAE)\n")
    f.write(f"- **Heart Rate MAE**: `{mean_hr_err:.2f} BPM`\n")
    f.write(f"- **Systolic BP (SBP) MAE**: `{mean_sbp_err:.2f} mmHg`\n")
    f.write(f"- **Diastolic BP (DBP) MAE**: `{mean_dbp_err:.2f} mmHg`\n")

# Generate Comparison Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

subs = [r['subject'] for r in results]
x = np.arange(len(subs))
width = 0.35

# Plot BP
ax1.bar(x - width/2, [r['sbp_actual'] for r in results], width, label='Actual SBP', color='#2196F3')
ax1.bar(x + width/2, [r['sbp_pred'] for r in results], width, label='Pred SBP', color='#9C27B0')
ax1.set_ylabel('Blood Pressure (mmHg)')
ax1.set_title('Systolic BP (Actual vs Predicted)')
ax1.set_xticks(x)
ax1.set_xticklabels(subs)
ax1.legend()
ax1.grid(True, linestyle='--', alpha=0.5)

# Plot HR
ax2.bar(x - width/2, [r['hr_actual'] for r in results], width, label='Actual HR', color='#4CAF50')
ax2.bar(x + width/2, [r['hr_pred'] for r in results], width, label='Pred HR', color='#FF9800')
ax2.set_ylabel('Heart Rate (BPM)')
ax2.set_title('Heart Rate (Actual vs Predicted)')
ax2.set_xticks(x)
ax2.set_xticklabels(subs)
ax2.legend()
ax2.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plot_path = os.path.join(test_out_dir, "prediction_vs_actual.png")
plt.savefig(plot_path, dpi=300)
plt.close()

print(f"Benchmark Complete! Reports saved to:\n  - CSV: {csv_path}\n  - Markdown: {md_report_path}\n  - Plot: {plot_path}")
