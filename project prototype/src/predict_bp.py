import os
# Must be set before importing tensorflow
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import sys
import types
dummy = types.ModuleType('runtime_version')
dummy.Domain = type('Domain', (), {'PUBLIC': 1})
dummy.ValidateProtobufRuntimeVersion = lambda *args, **kwargs: None
sys.modules['google.protobuf.runtime_version'] = dummy
import google.protobuf
google.protobuf.runtime_version = dummy

import numpy as np
import pandas as pd
import tensorflow as tf
import tf_keras
import argparse
import sys

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description="Predict Blood Pressure from POS PPG signal.")
    parser.add_argument("--ppg_file", type=str, default=os.path.join(base_dir, "data", "ppg_output.npy"), help="Path to normalized PPG .npy file")
    parser.add_argument("--model_file", type=str, default=os.path.join(base_dir, "models", "lstm_ppg_nonmixed.h5"), help="Path to Keras model")
    parser.add_argument("--window_size", type=int, default=875, help="Expected sequence length by the model")
    parser.add_argument("--step_size", type=int, default=30, help="Step size for sliding window (~1 second at 30fps)")
    args = parser.parse_args()

    if not os.path.exists(args.ppg_file):
        print(f"Error: {args.ppg_file} not found.")
        sys.exit(1)
        
    if not os.path.exists(args.model_file):
        print(f"Error: {args.model_file} not found.")
        sys.exit(1)

    print("Loading normalized PPG signal...")
    ppg_signal = np.load(args.ppg_file)
    
    N = len(ppg_signal)
    print(f"Loaded {N} frames of PPG data.")
    
    if N < args.window_size:
        print(f"Error: Signal length ({N}) is shorter than model window size ({args.window_size}).")
        sys.exit(1)

    print("Generating overlapping sequences and evaluating Signal Quality Indices (SQI)...")
    windows = []
    start_indices = []
    rejected_count = 0
    
    import scipy.signal as signal
    import scipy.stats as stats
    
    fs = 125.0
    
    for i in range(0, N - args.window_size + 1, args.step_size):
        window = ppg_signal[i : i + args.window_size]
        
        # 1. Skewness and Kurtosis checks (check for clipping or noise artifacts)
        skew = stats.skew(window)
        kurt = stats.kurtosis(window)
        
        if abs(skew) > 2.0 or kurt > 5.0:
            rejected_count += 1
            continue
            
        # 2. Spectral Analysis (Dominant Peak and SNR)
        f, Pxx = signal.welch(window, fs=fs, nperseg=len(window))
        
        # Find dominant peak
        dominant_f = f[np.argmax(Pxx)]
        if dominant_f < 0.75 or dominant_f > 3.5:
            rejected_count += 1
            continue
            
        # Calculate SNR (Power in [0.75, 3.5] Hz vs power outside)
        signal_band = (f >= 0.75) & (f <= 3.5)
        noise_band = ~signal_band
        
        p_signal = np.sum(Pxx[signal_band])
        p_noise = np.sum(Pxx[noise_band])
        
        snr = p_signal / (p_noise + 1e-8)
        
        if snr < 2.0:
            rejected_count += 1
            continue
            
        # If all checks pass, append the window
        windows.append(window)
        start_indices.append(i)
        
    print(f"SQI Filtering Complete: {len(windows)} windows accepted, {rejected_count} rejected.")
    
    if len(windows) == 0:
        print("Error: No windows passed the quality threshold. Signal is too noisy.")
        sys.exit(1)
        
    # Shape needs to be (num_windows, 875, 1)
    X_test = np.array(windows)
    X_test = np.expand_dims(X_test, axis=-1)
    print(f"Prepared batch of shape: {X_test.shape}")

    print("Loading deep learning model...")
    # Load model with tf_keras
    model = tf_keras.models.load_model(args.model_file, compile=False)
    
    print("Running inference (Predicting SBP and DBP)...")
    predictions = model.predict(X_test)
    
    # The model outputs a list of 2 tensors: [(num_windows, 1), (num_windows, 1)]
    # Typically [SBP, DBP] based on standard dual-output BP networks
    sbp_preds = predictions[0].flatten()
    dbp_preds = predictions[1].flatten()
    
    # Generate time axis for predictions
    # Approximating time by using the center of the window
    fs = 125.0 # PPG is resampled to 125 Hz
    time_points = [(idx + args.window_size // 2) / fs for idx in start_indices]
    
    # Save predictions
    df_preds = pd.DataFrame({
        'time': time_points,
        'SBP': sbp_preds,
        'DBP': dbp_preds
    })
    
    out_csv = os.path.join(base_dir, "data", "bp_predictions.csv")
    df_preds.to_csv(out_csv, index=False)
    print(f"Predictions saved to {out_csv}")
    
    # Compute overall robust estimate
    mean_sbp = np.mean(sbp_preds)
    mean_dbp = np.mean(dbp_preds)
    std_sbp = np.std(sbp_preds)
    std_dbp = np.std(dbp_preds)
    
    if mean_sbp < 90 or mean_dbp < 60:
        category = "Low"
    elif mean_sbp < 120 and mean_dbp < 80:
        category = "Normal"
    elif mean_sbp < 140 or mean_dbp < 90:
        category = "High"
    else:
        category = "Very High"
        
    print("\n" + "="*50)
    print("FINAL BLOOD PRESSURE ESTIMATE")
    print(f"Systolic (SBP):  {mean_sbp:.1f} ± {std_sbp:.1f} mmHg")
    print(f"Diastolic (DBP): {mean_dbp:.1f} ± {std_dbp:.1f} mmHg")
    print(f"Category:        {category}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
