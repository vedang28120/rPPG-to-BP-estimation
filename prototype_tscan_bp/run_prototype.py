"""
End-to-End Prototype Pipeline: Multi-Extractor (TS-CAN, POS, CHROM, GREEN) -> MODEL-06 BP Estimation
Supports single extractor or simultaneous 4-way comparative evaluation.
"""
import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add repository root to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from prototype_tscan_bp.download_weights import setup_all_checkpoints
from prototype_tscan_bp.tscan_extractor import TSCANExtractor
from prototype_tscan_bp.classical_extractor import ClassicalRPPGExtractor
from prototype_tscan_bp.bp_estimator import BPEstimationEngine


def try_lookup_mcd_ground_truth(video_path):
    """Attempts to find ground truth BP and demographics from MCD db.csv."""
    try:
        from huggingface_hub import hf_hub_download
        db_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset')
        df = pd.read_csv(db_path)
        
        # Extract filename / subject id from path
        base_name = os.path.basename(video_path)
        parts = base_name.replace('.avi', '').replace('.mp4', '').split('_')
        if len(parts) >= 3 and parts[0].isdigit():
            pid = int(parts[0])
            step = parts[-1]  # 'before' or 'after'
            match = df[(df['patient_id'] == pid) & (df['step'] == step)]
            if len(match) > 0:
                row = match.iloc[0]
                return {
                    "patient_id": pid,
                    "step": step,
                    "age": float(row['age']) if not np.isnan(row['age']) else 25.0,
                    "gender": 1 if row['sex'] == 'M' else 0,
                    "sex_str": str(row['sex']),
                    "bmi": float(row['bmi']) if not np.isnan(row['bmi']) else 22.0,
                    "gt_sbp": float(row['upper_ap']) if not np.isnan(row['upper_ap']) else None,
                    "gt_dbp": float(row['lower_ap']) if not np.isnan(row['lower_ap']) else None,
                    "gt_hr": float(row['pulse']) if not np.isnan(row['pulse']) else None
                }
    except Exception:
        pass
    return None


def generate_comparative_plots(method_data, gt_info, save_path):
    """
    Generates a 4-panel multi-method comparative diagnostic visualization:
    1. Pulse waveforms overlay
    2. Frequency spectra (FFT) & HR detection
    3. Resampled normalized pulse waves (125 Hz)
    4. SBP / DBP bar comparison across extractors vs Ground Truth
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    colors = {
        'TS-CAN': '#00E676',
        'POS': '#2979FF',
        'CHROM': '#FF9100',
        'GREEN': '#9C27B0'
    }

    # Panel 1: Pulse Waveform Overlay (first 8 seconds)
    ax1 = axes[0, 0]
    for name, data in method_data.items():
        pulse = data['pulse']
        fps = data['fps']
        t_len = min(len(pulse), int(fps * 8))
        t = np.arange(t_len) / fps
        p_slice = pulse[:t_len]
        # Standardize for visual comparison
        p_norm = (p_slice - np.mean(p_slice)) / (np.std(p_slice) + 1e-6)
        ax1.plot(t, p_norm, label=f"{name} (HR: {data['bpm']:.1f})", color=colors.get(name, 'black'), lw=1.6, alpha=0.85)

    ax1.set_title("Normalized Pulse Waveform s(t) Comparison (First 8s)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Time (seconds)")
    ax1.set_ylabel("Standardized Amplitude (Z-score)")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', fontsize=9)

    # Panel 2: FFT Power Spectrum & HR Comparison
    ax2 = axes[0, 1]
    if gt_info and gt_info.get('gt_hr'):
        ax2.axvline(gt_info['gt_hr'], color='red', linestyle='--', lw=2.0, label=f"Ground Truth HR: {gt_info['gt_hr']:.1f} BPM", zorder=5)

    for name, data in method_data.items():
        pulse = data['pulse']
        fps = data['fps']
        N = len(pulse)
        freqs = np.fft.rfftfreq(N, 1.0 / fps)
        fft_vals = np.abs(np.fft.rfft(pulse))
        valid_idx = np.where((freqs >= 0.5) & (freqs <= 3.5))[0]
        if len(valid_idx) > 0:
            power = fft_vals[valid_idx] / (np.max(fft_vals[valid_idx]) + 1e-6)
            ax2.plot(freqs[valid_idx] * 60.0, power, label=f"{name} (Peak: {data['bpm']:.1f} BPM)", color=colors.get(name, 'gray'), lw=1.5, alpha=0.8)

    ax2.set_title("Cardiac Frequency Spectrum (FFT)", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Heart Rate (Beats Per Minute)")
    ax2.set_ylabel("Normalized Spectral Power")
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=9)

    # Panel 3: SBP Comparison Bar Chart
    ax3 = axes[1, 0]
    methods = list(method_data.keys())
    sbp_preds = [method_data[m]['bp']['sbp'] for m in methods]
    
    x = np.arange(len(methods))
    bars = ax3.bar(x, sbp_preds, color=[colors.get(m, '#455A64') for m in methods], alpha=0.85, width=0.55)
    for b in bars:
        ax3.annotate(f"{b.get_height():.1f} mmHg", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    if gt_info and gt_info.get('gt_sbp'):
        ax3.axhline(gt_info['gt_sbp'], color='red', linestyle='--', lw=2.0, label=f"Ground Truth SBP: {gt_info['gt_sbp']:.1f} mmHg")
        ax3.legend(loc='upper right')

    ax3.set_title("Systolic Blood Pressure (SBP) Estimation", fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(methods, fontsize=11, fontweight='bold')
    ax3.set_ylabel("Pressure (mmHg)")
    ax3.set_ylim(0, max(sbp_preds + ([gt_info['gt_sbp']] if gt_info and gt_info.get('gt_sbp') else [140])) * 1.25)
    ax3.grid(True, linestyle='--', alpha=0.5)

    # Panel 4: DBP Comparison Bar Chart
    ax4 = axes[1, 1]
    dbp_preds = [method_data[m]['bp']['dbp'] for m in methods]
    
    bars2 = ax4.bar(x, dbp_preds, color=[colors.get(m, '#455A64') for m in methods], alpha=0.85, width=0.55)
    for b in bars2:
        ax4.annotate(f"{b.get_height():.1f} mmHg", xy=(b.get_x() + b.get_width()/2, b.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    if gt_info and gt_info.get('gt_dbp'):
        ax4.axhline(gt_info['gt_dbp'], color='red', linestyle='--', lw=2.0, label=f"Ground Truth DBP: {gt_info['gt_dbp']:.1f} mmHg")
        ax4.legend(loc='upper right')

    ax4.set_title("Diastolic Blood Pressure (DBP) Estimation", fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(methods, fontsize=11, fontweight='bold')
    ax4.set_ylabel("Pressure (mmHg)")
    ax4.set_ylim(0, max(dbp_preds + ([gt_info['gt_dbp']] if gt_info and gt_info.get('gt_dbp') else [90])) * 1.3)
    ax4.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[OK] Comparative diagnostic plot saved to: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Multi-Extractor rPPG -> MODEL-06 BP Estimation Prototype")
    parser.add_argument("--video", type=str, required=True, help="Path to input facial video (.avi, .mp4)")
    parser.add_argument("--extractor", type=str, default="all", choices=["all", "tscan", "pos", "chrom", "green"],
                        help="Extraction method: 'all' (compare all 4), 'tscan', 'pos', 'chrom', or 'green'")
    parser.add_argument("--age", type=float, default=20.0, help="Patient age in years (default: 20)")
    parser.add_argument("--gender", type=int, default=1, help="Patient gender: 1 for Male, 0 for Female (default: 1)")
    parser.add_argument("--bmi", type=float, default=21.0, help="Patient BMI in kg/m^2 (default: 21.0)")
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu", "cuda"], help="Inference device (cpu or cuda)")
    parser.add_argument("--save_plot", action="store_true", default=True, help="Save diagnostic visualization plot")
    args = parser.parse_args()

    print("=" * 80)
    print("       MULTI-EXTRACTOR rPPG -> MODEL-06 BLOOD PRESSURE ESTIMATION        ")
    print("=" * 80)

    # Step 0: Checkpoints setup
    tscan_ckpt, bp_ckpt = setup_all_checkpoints()

    # MCD Ground truth lookup
    gt_info = try_lookup_mcd_ground_truth(args.video)
    if gt_info:
        print(f"[OK] Detected MCD Ground Truth metadata for Subject {gt_info['patient_id']} ({gt_info['step']}):")
        print(f"    - Demographic: Age={gt_info['age']}, Sex={gt_info['sex_str']}, BMI={gt_info['bmi']:.1f}")
        print(f"    - True BP: SBP={gt_info['gt_sbp']} mmHg, DBP={gt_info['gt_dbp']} mmHg | True HR={gt_info['gt_hr']} BPM")
        age = gt_info['age']
        gender = gt_info['gender']
        bmi = gt_info['bmi']
    else:
        age = args.age
        gender = args.gender
        bmi = args.bmi

    # Step 1: Initialize BP Engine
    print(f"\n[*] Initializing MODEL-06 Blood Pressure Engine...")
    bp_engine = BPEstimationEngine(checkpoint_path=bp_ckpt, device=args.device)

    # Determine extractors to run
    extractors_to_run = ["TS-CAN", "POS", "CHROM", "GREEN"] if args.extractor == "all" else [args.extractor.upper()]
    results_map = {}

    # Initialize extractors
    tscan_extractor = None
    classical_extractor = None

    if "TS-CAN" in extractors_to_run:
        print(f"[*] Initializing TS-CAN Deep Neural Extractor...")
        tscan_extractor = TSCANExtractor(checkpoint_path=tscan_ckpt, device=args.device)

    if any(m in extractors_to_run for m in ["POS", "CHROM", "GREEN"]):
        print(f"[*] Initializing Classical FaceMesh Multi-ROI Extractor (POS/CHROM/GREEN)...")
        classical_extractor = ClassicalRPPGExtractor(method="pos")

    print(f"\n[*] Processing Video: {args.video}...")

    # Extract & Predict
    for method in extractors_to_run:
        print(f"\n---> Running Extractor: [{method}]")
        if method == "TS-CAN":
            pulse, fps, bpm, resp = tscan_extractor.process_video(args.video, max_duration_sec=30.0)
        else:
            pulse, fps, bpm, _ = classical_extractor.process_video(args.video, method=method.lower(), max_duration_sec=30.0)

        print(f"     [OK] Extracted {len(pulse)} samples at {fps:.1f} FPS | Estimated HR: {bpm:.1f} BPM")
        
        # Predict BP with MODEL-06
        bp_pred = bp_engine.predict_bp(pulse, source_fs=fps, age=age, gender=gender, bmi=bmi, window_sec=7.0)
        print(f"     -> MODEL-06 BP Prediction: SBP={bp_pred['sbp']:.1f} mmHg, DBP={bp_pred['dbp']:.1f} mmHg (MAP={bp_pred['map']:.1f} mmHg)")

        results_map[method] = {
            'pulse': pulse,
            'fps': fps,
            'bpm': bpm,
            'bp': bp_pred
        }

    if classical_extractor:
        classical_extractor.close()

    # Step 2: Print Comparative Summary Table
    print("\n" + "=" * 90)
    print("                     EXTRACTOR COMPARISON RESULTS TABLE                          ")
    print("=" * 90)
    header = f"{'Method':<12} | {'SBP (mmHg)':<12} | {'DBP (mmHg)':<12} | {'MAP (mmHg)':<12} | {'HR (BPM)':<10}"
    if gt_info:
        header += f" | {'SBP Err':<9} | {'DBP Err':<9} | {'HR Err':<9}"
    print(header)
    print("-" * len(header))

    if gt_info:
        gt_sbp = gt_info.get('gt_sbp')
        gt_dbp = gt_info.get('gt_dbp')
        gt_map = gt_dbp + (gt_sbp - gt_dbp) / 3.0 if (gt_sbp and gt_dbp) else None
        gt_hr = gt_info.get('gt_hr')
        gt_sbp_str = f"{gt_sbp:.1f}" if gt_sbp else "N/A"
        gt_dbp_str = f"{gt_dbp:.1f}" if gt_dbp else "N/A"
        gt_map_str = f"{gt_map:.1f}" if gt_map else "N/A"
        gt_hr_str = f"{gt_hr:.1f}" if gt_hr else "N/A"
        print(f"{'GROUND TRUTH':<12} | {gt_sbp_str:<12} | {gt_dbp_str:<12} | {gt_map_str:<12} | {gt_hr_str:<10} | {'-':<9} | {'-':<9} | {'-':<9}")
        print("-" * len(header))

    for method, data in results_map.items():
        sbp = data['bp']['sbp']
        dbp = data['bp']['dbp']
        map_val = data['bp']['map']
        bpm = data['bpm']
        line = f"{method:<12} | {sbp:<12.1f} | {dbp:<12.1f} | {map_val:<12.1f} | {bpm:<10.1f}"
        if gt_info:
            sbp_err = f"{abs(sbp - gt_info['gt_sbp']):.1f}" if gt_info.get('gt_sbp') else "N/A"
            dbp_err = f"{abs(dbp - gt_info['gt_dbp']):.1f}" if gt_info.get('gt_dbp') else "N/A"
            hr_err = f"{abs(bpm - gt_info['gt_hr']):.1f}" if gt_info.get('gt_hr') else "N/A"
            line += f" | {sbp_err:<9} | {dbp_err:<9} | {hr_err:<9}"
        print(line)
    print("=" * 90)

    # Step 3: Diagnostic Plots
    if args.save_plot:
        out_dir = os.path.join(current_dir, "results")
        os.makedirs(out_dir, exist_ok=True)
        vid_tag = os.path.basename(args.video).split('.')[0]
        plot_path = os.path.join(out_dir, f"extractor_comparison_{vid_tag}.png")
        generate_comparative_plots(results_map, gt_info, plot_path)


if __name__ == "__main__":
    main()
