"""
Blood Pressure Inference Engine
Loads normalized 125 Hz PPG waveforms, executes SQI filtering, performs neural inference, and computes clinical classification.
"""

import os
import argparse
import sys
import numpy as np
import pandas as pd
import torch

# Handle legacy Keras fallback if needed
os.environ['TF_USE_LEGACY_KERAS'] = '1'

def run_inference(ppg_path, checkpoint_path, window_size=875, step_size=30, fs=125.0):
    if not os.path.exists(ppg_path):
        raise FileNotFoundError(f"PPG file not found: {ppg_path}")
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    print(f"[INFERENCE] Loading PPG signal from: {ppg_path}")
    ppg_signal = np.load(ppg_path)
    n_samples = len(ppg_signal)
    print(f"[INFERENCE] Signal length: {n_samples} samples ({n_samples / fs:.2f} seconds)")

    if n_samples < window_size:
        raise ValueError(f"Signal length ({n_samples}) is shorter than required window ({window_size})")

    # SQI Filtering & Windowing
    from filtering.sqi_validator import evaluate_window_sqi
    windows = []
    start_indices = []
    rejected_count = 0

    for i in range(0, n_samples - window_size + 1, step_size):
        w = ppg_signal[i : i + window_size]
        is_valid, _ = evaluate_window_sqi(w, fs=fs)
        if is_valid:
            windows.append(w)
            start_indices.append(i)
        else:
            rejected_count += 1

    print(f"[INFERENCE] SQI Filtering: {len(windows)} windows accepted, {rejected_count} rejected.")
    if len(windows) == 0:
        raise RuntimeError("Zero windows passed the signal quality threshold.")

    windows_arr = np.array(windows, dtype=np.float32)

    # Detect model type by extension
    if checkpoint_path.endswith('.pth'):
        print(f"[INFERENCE] Running PyTorch MODEL-06 inference from: {checkpoint_path}")
        from models.architectures.resnet_bigru_attn import DualBranchResNetBiGRUAttn
        
        # Windows format for 1D Conv: (Batch, In_Channels=1, Length)
        x_tensor = torch.tensor(windows_arr).unsqueeze(1)
        
        model = DualBranchResNetBiGRUAttn(in_channels=1, use_demo=False, use_separate_heads=True)
        checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
        
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'], strict=False)
        elif isinstance(checkpoint, dict):
            model.load_state_dict(checkpoint, strict=False)
            
        model.eval()
        with torch.no_grad():
            preds = model(x_tensor).numpy()
            
        sbp_preds = preds[:, 0]
        dbp_preds = preds[:, 1]
    else:
        print(f"[INFERENCE] Running Keras/TF LSTM inference from: {checkpoint_path}")
        import tf_keras
        x_keras = np.expand_dims(windows_arr, axis=-1)
        model = tf_keras.models.load_model(checkpoint_path, compile=False)
        predictions = model.predict(x_keras)
        
        if isinstance(predictions, list):
            sbp_preds = predictions[0].flatten()
            dbp_preds = predictions[1].flatten()
        else:
            sbp_preds = predictions[:, 0].flatten()
            dbp_preds = predictions[:, 1].flatten()

    time_points = [(idx + window_size // 2) / fs for idx in start_indices]
    df_preds = pd.DataFrame({
        'time_sec': time_points,
        'SBP': sbp_preds,
        'DBP': dbp_preds
    })

    mean_sbp = float(np.mean(sbp_preds))
    mean_dbp = float(np.mean(dbp_preds))
    std_sbp = float(np.std(sbp_preds))
    std_dbp = float(np.std(dbp_preds))

    if mean_sbp < 90 or mean_dbp < 60:
        category = "Low (Hypotension)"
    elif mean_sbp < 120 and mean_dbp < 80:
        category = "Normal (Normotensive)"
    elif mean_sbp < 140 or mean_dbp < 90:
        category = "Elevated / Pre-Hypertension"
    else:
        category = "High (Hypertension)"

    print("\n" + "=" * 55)
    print("           BLOOD PRESSURE ESTIMATION REPORT           ")
    print("=" * 55)
    print(f"Systolic Blood Pressure (SBP):  {mean_sbp:.1f} ± {std_sbp:.1f} mmHg")
    print(f"Diastolic Blood Pressure (DBP): {mean_dbp:.1f} ± {std_dbp:.1f} mmHg")
    print(f"Clinical Category:              {category}")
    print("=" * 55 + "\n")

    return df_preds, (mean_sbp, mean_dbp, category)

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_ppg = os.path.join(repo_root, 'data', 'processed', 'ppg_output.npy')
    default_model = os.path.join(repo_root, 'models', 'checkpoints', 'MODEL-06-SepHead_original.pth')
    default_out = os.path.join(repo_root, 'data', 'processed', 'bp_predictions.csv')

    parser = argparse.ArgumentParser(description="rPPG Blood Pressure Inference")
    parser.add_argument("--ppg_file", type=str, default=default_ppg, help="Path to input PPG npy array")
    parser.add_argument("--checkpoint", type=str, default=default_model, help="Path to .pth or .h5 checkpoint")
    parser.add_argument("--out_csv", type=str, default=default_out, help="Output predictions CSV path")
    args = parser.parse_args()

    # Fallback to legacy h5 if pth not found
    if not os.path.exists(args.checkpoint):
        fallback_h5 = os.path.join(repo_root, 'models', 'checkpoints', 'lstm_ppg_nonmixed.h5')
        if os.path.exists(fallback_h5):
            args.checkpoint = fallback_h5

    df_preds, _ = run_inference(args.ppg_file, args.checkpoint)
    df_preds.to_csv(args.out_csv, index=False)
    print(f"[SUCCESS] Exported predictions to: {args.out_csv}")

if __name__ == '__main__':
    main()
