"""
Comprehensive Evaluation: TS-CAN vs Classical (POS, CHROM, GREEN) on High Refresh Rate MCD-rPPG Videos
Videos:
  - 1020_FullHDwebcam_before.avi (Resting Baseline)
  - 1020_FullHDwebcam_after.avi (Post-Exercise Stress)
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt
from scipy.signal import welch

# Ensure repo root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from prototype_tscan_bp.tscan_extractor import TSCANExtractor
from prototype_tscan_bp.classical_extractor import ClassicalRPPGExtractor
from prototype_tscan_bp.bp_estimator import BPEstimationEngine


def compute_snr(signal, fs, hr_bpm, harmonic_half_width=0.15):
    """
    Computes rPPG Signal-to-Noise Ratio (SNR) in dB around fundamental heart rate frequency
    and first harmonic vs in-band noise (0.7 Hz - 3.5 Hz, i.e., 42 - 210 BPM).
    """
    nperseg = min(len(signal), int(fs * 10))
    if nperseg < int(fs * 2):
        return 0.0
    f, pxx = welch(signal, fs=fs, nperseg=nperseg)
    hr_f = hr_bpm / 60.0
    fund_mask = (f >= hr_f - harmonic_half_width) & (f <= hr_f + harmonic_half_width)
    harm_mask = (f >= 2 * hr_f - harmonic_half_width) & (f <= 2 * hr_f + harmonic_half_width)
    sig_mask = fund_mask | harm_mask
    in_band = (f >= 0.7) & (f <= 3.5)
    noise_mask = in_band & (~sig_mask)
    sig_power = np.sum(pxx[sig_mask])
    noise_power = np.sum(pxx[noise_mask])
    if noise_power <= 0 or sig_power <= 0:
        return 0.0
    return float(10 * np.log10(sig_power / noise_power))


def run_evaluation():
    print("=" * 85)
    print("   EVALUATION: TS-CAN vs. CLASSICAL rPPG EXTRACTION ON HIGH REFRESH RATE MCD VIDEOS")
    print("   Dataset: MCD-rPPG (Subject 1020 - FullHD Webcam 1080p/60Hz sensor)")
    print("=" * 85)

    vids = {
        'before': {
            'name': '1020_FullHDwebcam_before.avi',
            'path': r'C:\Users\simpl\Downloads\1020_FullHDwebcam_before.avi',
            'gt_sbp': 105.0,
            'gt_dbp': 78.0,
            'gt_hr': 83.0,
            'gt_spo2': 99.0,
            'gt_resp': 18.0,
            'age': 23.0,
            'gender': 0,  # Female
            'bmi': 19.031142,
            'weight': 55.0,
            'height': 170.0,
            'state': 'Resting / Baseline'
        },
        'after': {
            'name': '1020_FullHDwebcam_after.avi',
            'path': r'C:\Users\simpl\Downloads\1020_FullHDwebcam_after.avi',
            'gt_sbp': 113.0,
            'gt_dbp': 78.0,
            'gt_hr': 100.0,
            'gt_spo2': 98.0,
            'gt_resp': 19.0,
            'age': 23.0,
            'gender': 0,  # Female
            'bmi': 19.031142,
            'weight': 55.0,
            'height': 170.0,
            'state': 'Post-Exercise / Elevated HR & SBP'
        }
    }

    tscan_ckpt = os.path.join(current_dir, "checkpoints", "mtts_can.hdf5")
    bp_ckpt = r"C:\Users\simpl\Downloads\master roadmap models and results\MODEL-06_Phase3_Bayesian.pth"
    if not os.path.exists(bp_ckpt):
        bp_ckpt = os.path.join(repo_root, "models", "checkpoints", "MODEL-06-SepHead_original.pth")

    print(f"[*] Initializing TS-CAN Extractor from: {tscan_ckpt}")
    tscan_extractor = TSCANExtractor(checkpoint_path=tscan_ckpt, device="cpu")

    print("[*] Initializing Classical Extractors (POS, CHROM, GREEN)...")
    classical_pos = ClassicalRPPGExtractor(method="pos")
    classical_chrom = ClassicalRPPGExtractor(method="chrom")
    classical_green = ClassicalRPPGExtractor(method="green")

    print(f"[*] Initializing MODEL-06 BP Engine from: {bp_ckpt}")
    bp_engine = BPEstimationEngine(checkpoint_path=bp_ckpt, device="cpu")

    duration_sec = 30.0
    results = {}
    signals_dict = {}

    for trial_key, meta in vids.items():
        vid_path = meta['path']
        print(f"\n" + "-" * 75)
        print(f">>> Evaluating Trial: {trial_key.upper()} ({meta['name']})")
        print(f"    Clinical State: {meta['state']}")
        print(f"    Demographics: Age {meta['age']}y | Female | BMI {meta['bmi']:.1f} (55kg, 170cm)")
        print(f"    Ground Truth: SBP = {meta['gt_sbp']} mmHg | DBP = {meta['gt_dbp']} mmHg | HR = {meta['gt_hr']} BPM | SpO2 = {meta['gt_spo2']}%")
        print("-" * 75)

        cap = cv2.VideoCapture(vid_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        if fps <= 0 or np.isnan(fps):
            fps = 30.0

        trial_results = {}
        trial_signals = {}

        # 1. TS-CAN
        print("  [1/4] Running TS-CAN (Temporal Shift Attention Network)...")
        t0 = time.time()
        pulse_tscan, fs_tscan, hr_tscan, resp_tscan = tscan_extractor.process_video(vid_path, max_duration_sec=duration_sec)
        t_tscan = time.time() - t0
        bp_tscan = bp_engine.predict_bp(pulse_tscan, source_fs=fs_tscan, age=meta['age'], gender=meta['gender'], bmi=meta['bmi'])
        snr_tscan = compute_snr(pulse_tscan, fs_tscan, hr_tscan)

        trial_results['TS-CAN'] = {
            'hr': round(hr_tscan, 1),
            'hr_err': round(abs(hr_tscan - meta['gt_hr']), 2),
            'sbp': round(bp_tscan['sbp'], 1),
            'sbp_err': round(abs(bp_tscan['sbp'] - meta['gt_sbp']), 2),
            'dbp': round(bp_tscan['dbp'], 1),
            'dbp_err': round(abs(bp_tscan['dbp'] - meta['gt_dbp']), 2),
            'map': round(bp_tscan['map'], 1),
            'map_err': round(abs(bp_tscan['map'] - (meta['gt_dbp'] + (meta['gt_sbp'] - meta['gt_dbp']) / 3.0)), 2),
            'pp': round(bp_tscan['pulse_pressure'], 1),
            'pp_err': round(abs(bp_tscan['pulse_pressure'] - (meta['gt_sbp'] - meta['gt_dbp'])), 2),
            'snr_db': round(snr_tscan, 2),
            'latency_s': round(t_tscan, 2),
            'fps': fs_tscan
        }
        trial_signals['TS-CAN'] = pulse_tscan

        # 2. POS
        print("  [2/4] Running Classical POS (Plane-Orthogonal-to-Skin)...")
        t0 = time.time()
        pulse_pos, fs_pos, hr_pos, _ = classical_pos.process_video(vid_path, method="pos", max_duration_sec=duration_sec)
        t_pos = time.time() - t0
        bp_pos = bp_engine.predict_bp(pulse_pos, source_fs=fs_pos, age=meta['age'], gender=meta['gender'], bmi=meta['bmi'])
        snr_pos = compute_snr(pulse_pos, fs_pos, hr_pos)

        trial_results['POS'] = {
            'hr': round(hr_pos, 1),
            'hr_err': round(abs(hr_pos - meta['gt_hr']), 2),
            'sbp': round(bp_pos['sbp'], 1),
            'sbp_err': round(abs(bp_pos['sbp'] - meta['gt_sbp']), 2),
            'dbp': round(bp_pos['dbp'], 1),
            'dbp_err': round(abs(bp_pos['dbp'] - meta['gt_dbp']), 2),
            'map': round(bp_pos['map'], 1),
            'map_err': round(abs(bp_pos['map'] - (meta['gt_dbp'] + (meta['gt_sbp'] - meta['gt_dbp']) / 3.0)), 2),
            'pp': round(bp_pos['pulse_pressure'], 1),
            'pp_err': round(abs(bp_pos['pulse_pressure'] - (meta['gt_sbp'] - meta['gt_dbp'])), 2),
            'snr_db': round(snr_pos, 2),
            'latency_s': round(t_pos, 2),
            'fps': fs_pos
        }
        trial_signals['POS'] = pulse_pos

        # 3. CHROM
        print("  [3/4] Running Classical CHROM (Chrominance-based)...")
        t0 = time.time()
        pulse_chrom, fs_chrom, hr_chrom, _ = classical_chrom.process_video(vid_path, method="chrom", max_duration_sec=duration_sec)
        t_chrom = time.time() - t0
        bp_chrom = bp_engine.predict_bp(pulse_chrom, source_fs=fs_chrom, age=meta['age'], gender=meta['gender'], bmi=meta['bmi'])
        snr_chrom = compute_snr(pulse_chrom, fs_chrom, hr_chrom)

        trial_results['CHROM'] = {
            'hr': round(hr_chrom, 1),
            'hr_err': round(abs(hr_chrom - meta['gt_hr']), 2),
            'sbp': round(bp_chrom['sbp'], 1),
            'sbp_err': round(abs(bp_chrom['sbp'] - meta['gt_sbp']), 2),
            'dbp': round(bp_chrom['dbp'], 1),
            'dbp_err': round(abs(bp_chrom['dbp'] - meta['gt_dbp']), 2),
            'map': round(bp_chrom['map'], 1),
            'map_err': round(abs(bp_chrom['map'] - (meta['gt_dbp'] + (meta['gt_sbp'] - meta['gt_dbp']) / 3.0)), 2),
            'pp': round(bp_chrom['pulse_pressure'], 1),
            'pp_err': round(abs(bp_chrom['pulse_pressure'] - (meta['gt_sbp'] - meta['gt_dbp'])), 2),
            'snr_db': round(snr_chrom, 2),
            'latency_s': round(t_chrom, 2),
            'fps': fs_chrom
        }
        trial_signals['CHROM'] = pulse_chrom

        # 4. GREEN
        print("  [4/4] Running Classical GREEN (Green Channel Averaging)...")
        t0 = time.time()
        pulse_green, fs_green, hr_green, _ = classical_green.process_video(vid_path, method="green", max_duration_sec=duration_sec)
        t_green = time.time() - t0
        bp_green = bp_engine.predict_bp(pulse_green, source_fs=fs_green, age=meta['age'], gender=meta['gender'], bmi=meta['bmi'])
        snr_green = compute_snr(pulse_green, fs_green, hr_green)

        trial_results['GREEN'] = {
            'hr': round(hr_green, 1),
            'hr_err': round(abs(hr_green - meta['gt_hr']), 2),
            'sbp': round(bp_green['sbp'], 1),
            'sbp_err': round(abs(bp_green['sbp'] - meta['gt_sbp']), 2),
            'dbp': round(bp_green['dbp'], 1),
            'dbp_err': round(abs(bp_green['dbp'] - meta['gt_dbp']), 2),
            'map': round(bp_green['map'], 1),
            'map_err': round(abs(bp_green['map'] - (meta['gt_dbp'] + (meta['gt_sbp'] - meta['gt_dbp']) / 3.0)), 2),
            'pp': round(bp_green['pulse_pressure'], 1),
            'pp_err': round(abs(bp_green['pulse_pressure'] - (meta['gt_sbp'] - meta['gt_dbp'])), 2),
            'snr_db': round(snr_green, 2),
            'latency_s': round(t_green, 2),
            'fps': fs_green
        }
        trial_signals['GREEN'] = pulse_green

        results[trial_key] = {
            'meta': {k: v for k, v in meta.items() if k != 'path'},
            'methods': trial_results
        }
        signals_dict[trial_key] = trial_signals

    # Print comparative tables
    print("\n" + "=" * 105)
    print("                      ACCURACY & PERFORMANCE COMPARISON REPORT")
    print("=" * 105)
    for trial_key, data in results.items():
        meta = data['meta']
        gt_map = meta['gt_dbp'] + (meta['gt_sbp'] - meta['gt_dbp']) / 3.0
        print(f"\n>>> TRIAL: {trial_key.upper()} ({meta['state']})")
        print(f"    Clinical Ground Truth: SBP = {meta['gt_sbp']} mmHg | DBP = {meta['gt_dbp']} mmHg | MAP = {gt_map:.1f} mmHg | HR = {meta['gt_hr']} BPM")
        print("-" * 105)
        print(f"{'Method':<10} | {'HR (BPM)':<10} | {'HR Err':<8} | {'SBP (mmHg)':<11} | {'SBP Err':<8} | {'DBP (mmHg)':<11} | {'DBP Err':<8} | {'SNR (dB)':<9} | {'Time (s)':<8}")
        print("-" * 105)
        for method, m in data['methods'].items():
            print(f"{method:<10} | {m['hr']:<10.1f} | {m['hr_err']:<8.2f} | {m['sbp']:<11.1f} | {m['sbp_err']:<8.2f} | {m['dbp']:<11.1f} | {m['dbp_err']:<8.2f} | {m['snr_db']:<9.2f} | {m['latency_s']:<8.2f}")

    # Compute overall summary metrics across both trials
    print("\n" + "=" * 105)
    print("                 OVERALL MEAN ABSOLUTE ERRORS (MAE) ACROSS BOTH VIDEOS")
    print("=" * 105)
    methods = ['TS-CAN', 'POS', 'CHROM', 'GREEN']
    summary_data = []
    for m in methods:
        sbp_errors = [results[k]['methods'][m]['sbp_err'] for k in results]
        dbp_errors = [results[k]['methods'][m]['dbp_err'] for k in results]
        hr_errors = [results[k]['methods'][m]['hr_err'] for k in results]
        snrs = [results[k]['methods'][m]['snr_db'] for k in results]
        times = [results[k]['methods'][m]['latency_s'] for k in results]

        summary_data.append({
            'Method': m,
            'SBP MAE (mmHg)': round(np.mean(sbp_errors), 2),
            'DBP MAE (mmHg)': round(np.mean(dbp_errors), 2),
            'BP Overall MAE': round(np.mean(sbp_errors + dbp_errors), 2),
            'HR MAE (BPM)': round(np.mean(hr_errors), 2),
            'Mean SNR (dB)': round(np.mean(snrs), 2),
            'Mean Latency (s)': round(np.mean(times), 2)
        })

    df_summary = pd.DataFrame(summary_data)
    print(df_summary.to_string(index=False))

    # Save JSON and CSV
    out_dir = os.path.join(repo_root, "results")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "mcd_1020_accuracy_comparison.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2)
    csv_path = os.path.join(out_dir, "mcd_1020_accuracy_summary.csv")
    df_summary.to_csv(csv_path, index=False)
    print(f"\n[OK] Results saved to:\n  - {json_path}\n  - {csv_path}")

    # Generate Visualization Figure
    generate_comparison_plots(results, signals_dict, os.path.join(out_dir, "mcd_1020_accuracy_comparison.png"))


def generate_comparison_plots(results, signals_dict, out_path):
    fig, axes = plt.subplots(3, 2, figsize=(18, 14))
    methods = ['TS-CAN', 'POS', 'CHROM', 'GREEN']
    palette = {'TS-CAN': '#00E676', 'POS': '#2979FF', 'CHROM': '#FF9100', 'GREEN': '#9C27B0'}

    # 1. Waveforms for 'before' (First 6 seconds)
    ax1 = axes[0, 0]
    fs = 29.9
    samples = int(6.0 * fs)
    t = np.arange(samples) / fs
    for m in methods:
        sig = signals_dict['before'][m][:samples]
        sig_norm = (sig - np.mean(sig)) / (np.std(sig) + 1e-6)
        ax1.plot(t, sig_norm + (methods.index(m) * 3.5), label=m, color=palette[m], lw=1.8)
    ax1.set_title("Waveform Morphology: Subject 1020 Before (Resting, GT HR=83 BPM)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Normalized Amplitude (offset)")
    ax1.legend(loc="upper right")
    ax1.grid(True, linestyle="--", alpha=0.4)

    # 2. Waveforms for 'after' (First 6 seconds)
    ax2 = axes[0, 1]
    for m in methods:
        sig = signals_dict['after'][m][:samples]
        sig_norm = (sig - np.mean(sig)) / (np.std(sig) + 1e-6)
        ax2.plot(t, sig_norm + (methods.index(m) * 3.5), label=m, color=palette[m], lw=1.8)
    ax2.set_title("Waveform Morphology: Subject 1020 After (Post-Exercise, GT HR=100 BPM)", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Time (seconds)")
    ax2.set_ylabel("Normalized Amplitude (offset)")
    ax2.legend(loc="upper right")
    ax2.grid(True, linestyle="--", alpha=0.4)

    # 3. SBP Estimation Comparison (Before & After)
    ax3 = axes[1, 0]
    x = np.arange(len(methods))
    w = 0.35
    sbp_before = [results['before']['methods'][m]['sbp'] for m in methods]
    sbp_after = [results['after']['methods'][m]['sbp'] for m in methods]
    ax3.bar(x - w/2, sbp_before, w, label='Before Pred', color='#42A5F5', alpha=0.85)
    ax3.bar(x + w/2, sbp_after, w, label='After Pred', color='#EF5350', alpha=0.85)
    ax3.axhline(results['before']['meta']['gt_sbp'], color='#1565C0', linestyle='--', lw=2, label=f"GT SBP Before ({results['before']['meta']['gt_sbp']} mmHg)")
    ax3.axhline(results['after']['meta']['gt_sbp'], color='#C62828', linestyle='--', lw=2, label=f"GT SBP After ({results['after']['meta']['gt_sbp']} mmHg)")
    ax3.set_title("Systolic Blood Pressure (SBP) Prediction vs Ground Truth", fontsize=11, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, fontweight='bold')
    ax3.set_ylabel("SBP (mmHg)")
    ax3.set_ylim(80, 130)
    ax3.legend(loc="lower right", fontsize=9)
    ax3.grid(True, linestyle="--", alpha=0.4)

    # 4. DBP Estimation Comparison (Before & After)
    ax4 = axes[1, 1]
    dbp_before = [results['before']['methods'][m]['dbp'] for m in methods]
    dbp_after = [results['after']['methods'][m]['dbp'] for m in methods]
    ax4.bar(x - w/2, dbp_before, w, label='Before Pred', color='#26A69A', alpha=0.85)
    ax4.bar(x + w/2, dbp_after, w, label='After Pred', color='#AB47BC', alpha=0.85)
    ax4.axhline(results['before']['meta']['gt_dbp'], color='#004D40', linestyle='--', lw=2, label=f"GT DBP ({results['before']['meta']['gt_dbp']} mmHg)")
    ax4.set_title("Diastolic Blood Pressure (DBP) Prediction vs Ground Truth", fontsize=11, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(methods, fontweight='bold')
    ax4.set_ylabel("DBP (mmHg)")
    ax4.set_ylim(60, 95)
    ax4.legend(loc="lower right", fontsize=9)
    ax4.grid(True, linestyle="--", alpha=0.4)

    # 5. SBP & DBP MAE Error by Method
    ax5 = axes[2, 0]
    sbp_maes = [np.mean([results['before']['methods'][m]['sbp_err'], results['after']['methods'][m]['sbp_err']]) for m in methods]
    dbp_maes = [np.mean([results['before']['methods'][m]['dbp_err'], results['after']['methods'][m]['dbp_err']]) for m in methods]
    r1 = ax5.bar(x - w/2, sbp_maes, w, label='SBP MAE (mmHg)', color='#FF7043', alpha=0.85)
    r2 = ax5.bar(x + w/2, dbp_maes, w, label='DBP MAE (mmHg)', color='#5C6BC0', alpha=0.85)
    ax5.axhline(8.0, color='red', linestyle='--', label='AAMI Clinical Standard (8.0 mmHg)')
    for r in list(r1) + list(r2):
        ax5.annotate(f"{r.get_height():.2f}", xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax5.set_title("Mean Absolute Error (MAE): SBP & DBP Across Both Videos", fontsize=11, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(methods, fontweight='bold')
    ax5.set_ylabel("Absolute Error (mmHg)")
    ax5.set_ylim(0, max(sbp_maes + dbp_maes) * 1.35)
    ax5.legend(loc="upper right", fontsize=9)
    ax5.grid(True, linestyle="--", alpha=0.4)

    # 6. Heart Rate Error & SNR
    ax6 = axes[2, 1]
    hr_maes = [np.mean([results['before']['methods'][m]['hr_err'], results['after']['methods'][m]['hr_err']]) for m in methods]
    snr_means = [np.mean([results['before']['methods'][m]['snr_db'], results['after']['methods'][m]['snr_db']]) for m in methods]
    ax6_twin = ax6.twinx()
    b1 = ax6.bar(x - w/2, hr_maes, w, label='HR MAE (BPM)', color='#43A047', alpha=0.85)
    b2 = ax6_twin.bar(x + w/2, snr_means, w, label='SNR (dB)', color='#FB8C00', alpha=0.85)
    ax6.set_ylabel("Heart Rate Error (BPM)", color='#2E7D32', fontweight='bold')
    ax6_twin.set_ylabel("Signal-to-Noise Ratio (dB)", color='#E65100', fontweight='bold')
    ax6.set_title("Heart Rate Error & Signal Quality (SNR)", fontsize=11, fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels(methods, fontweight='bold')
    ax6.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"[OK] High-resolution visualization plot saved to: {out_path}")


if __name__ == "__main__":
    run_evaluation()
