"""
Batch Comparative Benchmark Script: TS-CAN vs. POS vs. CHROM vs. GREEN + MODEL-06 BP Estimation
Evaluates all four facial rPPG extraction pipelines on clinical MCD trials against ground truth.
"""
import os
import sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from huggingface_hub import hf_hub_download

# Add root directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from prototype_tscan_bp.download_weights import setup_all_checkpoints
from prototype_tscan_bp.tscan_extractor import TSCANExtractor
from prototype_tscan_bp.classical_extractor import ClassicalRPPGExtractor
from prototype_tscan_bp.bp_estimator import BPEstimationEngine


def method_col(method_name):
    """Normalizes method display name to dataframe column prefix."""
    return method_name.lower().replace("-", "").replace(" ", "_")


def compute_metrics(df_sub, method_name):
    """Computes comprehensive error and clinical standard metrics for an extractor."""
    col_prefix = method_col(method_name)
    gt_sbp = df_sub['gt_sbp'].values
    pred_sbp = df_sub[f'{col_prefix}_sbp'].values
    gt_dbp = df_sub['gt_dbp'].values
    pred_dbp = df_sub[f'{col_prefix}_dbp'].values
    
    # SBP metrics
    err_sbp = np.abs(pred_sbp - gt_sbp)
    mae_sbp = float(np.mean(err_sbp))
    rmse_sbp = float(np.sqrt(np.mean((pred_sbp - gt_sbp)**2)))
    bias_sbp = float(np.mean(pred_sbp - gt_sbp))
    sd_sbp = float(np.std(pred_sbp - gt_sbp))
    r_sbp = float(np.corrcoef(gt_sbp, pred_sbp)[0, 1]) if len(gt_sbp) > 1 else 0.0
    pct_5_sbp = float(np.mean(err_sbp <= 5.0) * 100.0)
    pct_10_sbp = float(np.mean(err_sbp <= 10.0) * 100.0)
    pct_15_sbp = float(np.mean(err_sbp <= 15.0) * 100.0)

    # DBP metrics
    err_dbp = np.abs(pred_dbp - gt_dbp)
    mae_dbp = float(np.mean(err_dbp))
    rmse_dbp = float(np.sqrt(np.mean((pred_dbp - gt_dbp)**2)))
    bias_dbp = float(np.mean(pred_dbp - gt_dbp))
    sd_dbp = float(np.std(pred_dbp - gt_dbp))
    r_dbp = float(np.corrcoef(gt_dbp, pred_dbp)[0, 1]) if len(gt_dbp) > 1 else 0.0
    pct_5_dbp = float(np.mean(err_dbp <= 5.0) * 100.0)
    pct_10_dbp = float(np.mean(err_dbp <= 10.0) * 100.0)
    pct_15_dbp = float(np.mean(err_dbp <= 15.0) * 100.0)

    # HR metrics (if ground truth available)
    valid_hr = df_sub[df_sub['gt_hr'].notnull()]
    if len(valid_hr) > 0:
        gt_hr = valid_hr['gt_hr'].values
        pred_hr = valid_hr[f'{col_prefix}_hr'].values
        err_hr = np.abs(pred_hr - gt_hr)
        mae_hr = float(np.mean(err_hr))
        rmse_hr = float(np.sqrt(np.mean((pred_hr - gt_hr)**2)))
        r_hr = float(np.corrcoef(gt_hr, pred_hr)[0, 1]) if len(gt_hr) > 1 else 0.0
    else:
        mae_hr, rmse_hr, r_hr = 0.0, 0.0, 0.0

    return {
        'method': method_name,
        'mae_sbp': mae_sbp, 'rmse_sbp': rmse_sbp, 'bias_sbp': bias_sbp, 'sd_sbp': sd_sbp, 'r_sbp': r_sbp,
        'pct_5_sbp': pct_5_sbp, 'pct_10_sbp': pct_10_sbp, 'pct_15_sbp': pct_15_sbp,
        'mae_dbp': mae_dbp, 'rmse_dbp': rmse_dbp, 'bias_dbp': bias_dbp, 'sd_dbp': sd_dbp, 'r_dbp': r_dbp,
        'pct_5_dbp': pct_5_dbp, 'pct_10_dbp': pct_10_dbp, 'pct_15_dbp': pct_15_dbp,
        'mae_hr': mae_hr, 'rmse_hr': rmse_hr, 'r_hr': r_hr
    }


def generate_benchmark_summary_plots(df_res, metrics_dict, out_fig_path):
    """Generates comparative boxplots, bar plots, and Bland-Altman charts."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    methods = ['TS-CAN', 'POS', 'CHROM', 'GREEN']
    palette = ['#00E676', '#2979FF', '#FF9100', '#9C27B0']

    # Panel 1: SBP & DBP MAE Comparison
    ax1 = axes[0, 0]
    sbp_maes = [metrics_dict[m]['mae_sbp'] for m in methods]
    dbp_maes = [metrics_dict[m]['mae_dbp'] for m in methods]
    x = np.arange(len(methods))
    width = 0.35

    rects1 = ax1.bar(x - width/2, sbp_maes, width, label='SBP MAE', color='#E91E63', alpha=0.85)
    rects2 = ax1.bar(x + width/2, dbp_maes, width, label='DBP MAE', color='#3F51B5', alpha=0.85)
    ax1.axhline(8.0, color='gray', linestyle='--', label='AAMI Standard (8.0 mmHg)')

    for r in rects1:
        ax1.annotate(f'{r.get_height():.2f}', xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
    for r in rects2:
        ax1.annotate(f'{r.get_height():.2f}', xy=(r.get_x() + r.get_width()/2, r.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

    ax1.set_title("Blood Pressure Mean Absolute Error (MAE in mmHg)", fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=11, fontweight='bold')
    ax1.set_ylabel("Mean Absolute Error (mmHg)")
    ax1.set_ylim(0, max(sbp_maes + dbp_maes) * 1.3)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    # Panel 2: Heart Rate MAE Comparison
    ax2 = axes[0, 1]
    hr_maes = [metrics_dict[m]['mae_hr'] for m in methods]
    bars_hr = ax2.bar(methods, hr_maes, color=palette, alpha=0.85, width=0.5)
    for b in bars_hr:
        ax2.annotate(f'{b.get_height():.2f} BPM', xy=(b.get_x() + b.get_width()/2, b.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax2.set_title("Heart Rate Mean Absolute Error (MAE in BPM)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("HR Error (BPM)")
    ax2.set_ylim(0, max(hr_maes) * 1.35)
    ax2.grid(True, linestyle='--', alpha=0.5)

    # Panel 3: SBP Error Boxplots
    ax3 = axes[1, 0]
    sbp_err_data = [np.abs(df_res[f'{method_col(m)}_sbp'] - df_res['gt_sbp']) for m in methods]
    box3 = ax3.boxplot(sbp_err_data, patch_artist=True, labels=methods, widths=0.5)
    for patch, color in zip(box3['boxes'], palette):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax3.axhline(8.0, color='red', linestyle='--', label='AAMI Error Limit (8 mmHg)')
    ax3.set_title("SBP Absolute Error Distributions", fontsize=12, fontweight='bold')
    ax3.set_ylabel("Absolute Error (mmHg)")
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc='upper right')

    # Panel 4: Cumulative Accuracy <= 5, 10, 15 mmHg
    ax4 = axes[1, 1]
    pct5 = [metrics_dict[m]['pct_5_sbp'] for m in methods]
    pct10 = [metrics_dict[m]['pct_10_sbp'] for m in methods]
    pct15 = [metrics_dict[m]['pct_15_sbp'] for m in methods]
    
    w = 0.25
    x4 = np.arange(len(methods))
    ax4.bar(x4 - w, pct5, w, label='Error <= 5 mmHg', color='#4CAF50', alpha=0.85)
    ax4.bar(x4, pct10, w, label='Error <= 10 mmHg', color='#FF9800', alpha=0.85)
    ax4.bar(x4 + w, pct15, w, label='Error <= 15 mmHg', color='#2196F3', alpha=0.85)

    ax4.set_title("SBP Cumulative Clinical Accuracy Rates (%)", fontsize=12, fontweight='bold')
    ax4.set_xticks(x4)
    ax4.set_xticklabels(methods, fontsize=11, fontweight='bold')
    ax4.set_ylabel("Percentage of Trials (%)")
    ax4.set_ylim(0, 110)
    ax4.grid(True, linestyle='--', alpha=0.5)
    ax4.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(out_fig_path, dpi=300)
    plt.close()
    print(f"[OK] Summary comparison plots saved to: {out_fig_path}")


def run_comparative_benchmark(num_trials=16, max_sec=15.0):
    print("=" * 85)
    print(f"   COMPREHENSIVE 4-WAY rPPG BENCHMARK: TS-CAN vs. POS vs. CHROM vs. GREEN   ")
    print(f"   Evaluating on {num_trials} MCD Clinical Video Trials with MODEL-06 BP Engine   ")
    print("=" * 85)

    # 1. Download database CSV and get ground truth entries
    db_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset')
    df = pd.read_csv(db_path)
    df_valid = df[(df['upper_ap'].notnull()) & (df['lower_ap'].notnull())].drop_duplicates(subset=['patient_id', 'step']).copy()

    # 2. Setup model checkpoints and extractors
    tscan_ckpt, bp_ckpt = setup_all_checkpoints()
    tscan_extractor = TSCANExtractor(checkpoint_path=tscan_ckpt, device='cpu')
    classical_extractor = ClassicalRPPGExtractor(method='pos')
    bp_engine = BPEstimationEngine(checkpoint_path=bp_ckpt, device='cpu')

    mcd_dir = r"E:\VT\PPG rPPG BP project\MCD_rppg"
    results = []
    processed = 0

    methods = ['TS-CAN', 'POS', 'CHROM', 'GREEN']
    timing_data = {m: [] for m in methods}

    for idx, row in df_valid.iterrows():
        if processed >= num_trials:
            break
        pid = int(row['patient_id'])
        step = str(row['step'])

        sub_dir = os.path.join(mcd_dir, f"Subject_{pid}")
        vid_path = os.path.join(sub_dir, "video", "video", f"{pid}_IriunWebcam_{step}.avi")
        if not os.path.exists(vid_path):
            vid_path = os.path.join(sub_dir, "video", f"{pid}_IriunWebcam_{step}.avi")
        if not os.path.exists(vid_path):
            continue

        gt_sbp = float(row['upper_ap'])
        gt_dbp = float(row['lower_ap'])
        gt_hr = float(row['pulse']) if not np.isnan(row['pulse']) else None
        age = float(row['age']) if not np.isnan(row['age']) else 25.0
        gender = 1 if row['sex'] == 'M' else 0
        bmi = float(row['bmi']) if not np.isnan(row['bmi']) else 22.0

        trial_record = {
            'subject_id': pid,
            'step': step,
            'age': age,
            'gender': 'M' if gender == 1 else 'F',
            'bmi': round(bmi, 1),
            'gt_sbp': gt_sbp,
            'gt_dbp': gt_dbp,
            'gt_hr': gt_hr
        }

        print(f"\n[{processed+1:02d}/{num_trials}] Processing Subject {pid} ({step:<6}) | Ground Truth: SBP={gt_sbp:.1f}, DBP={gt_dbp:.1f}, HR={gt_hr}...")

        try:
            # 1. TS-CAN
            t0 = time.time()
            pulse_tscan, fps_tscan, bpm_tscan, _ = tscan_extractor.process_video(vid_path, max_duration_sec=max_sec)
            timing_data['TS-CAN'].append(time.time() - t0)
            pred_tscan = bp_engine.predict_bp(pulse_tscan, source_fs=fps_tscan, age=age, gender=gender, bmi=bmi)
            trial_record['tscan_sbp'] = pred_tscan['sbp']
            trial_record['tscan_dbp'] = pred_tscan['dbp']
            trial_record['tscan_hr'] = round(bpm_tscan, 1)

            # 2. POS
            t0 = time.time()
            pulse_pos, fps_pos, bpm_pos, rgb_traces = classical_extractor.process_video(vid_path, method='pos', max_duration_sec=max_sec)
            timing_data['POS'].append(time.time() - t0)
            pred_pos = bp_engine.predict_bp(pulse_pos, source_fs=fps_pos, age=age, gender=gender, bmi=bmi)
            trial_record['pos_sbp'] = pred_pos['sbp']
            trial_record['pos_dbp'] = pred_pos['dbp']
            trial_record['pos_hr'] = round(bpm_pos, 1)

            # 3. CHROM
            t0 = time.time()
            pulse_chrom, fps_chrom, bpm_chrom, _ = classical_extractor.process_video(vid_path, method='chrom', max_duration_sec=max_sec)
            timing_data['CHROM'].append(time.time() - t0)
            pred_chrom = bp_engine.predict_bp(pulse_chrom, source_fs=fps_chrom, age=age, gender=gender, bmi=bmi)
            trial_record['chrom_sbp'] = pred_chrom['sbp']
            trial_record['chrom_dbp'] = pred_chrom['dbp']
            trial_record['chrom_hr'] = round(bpm_chrom, 1)

            # 4. GREEN
            t0 = time.time()
            pulse_green, fps_green, bpm_green, _ = classical_extractor.process_video(vid_path, method='green', max_duration_sec=max_sec)
            timing_data['GREEN'].append(time.time() - t0)
            pred_green = bp_engine.predict_bp(pulse_green, source_fs=fps_green, age=age, gender=gender, bmi=bmi)
            trial_record['green_sbp'] = pred_green['sbp']
            trial_record['green_dbp'] = pred_green['dbp']
            trial_record['green_hr'] = round(bpm_green, 1)

            results.append(trial_record)
            processed += 1

            # Print concise trial summary
            print(f"    -> TS-CAN: SBP={pred_tscan['sbp']:.1f} (Err={abs(pred_tscan['sbp']-gt_sbp):.1f}) | HR={bpm_tscan:.1f}")
            print(f"    -> POS:    SBP={pred_pos['sbp']:.1f} (Err={abs(pred_pos['sbp']-gt_sbp):.1f}) | HR={bpm_pos:.1f}")
            print(f"    -> CHROM:  SBP={pred_chrom['sbp']:.1f} (Err={abs(pred_chrom['sbp']-gt_sbp):.1f}) | HR={bpm_chrom:.1f}")
            print(f"    -> GREEN:  SBP={pred_green['sbp']:.1f} (Err={abs(pred_green['sbp']-gt_sbp):.1f}) | HR={bpm_green:.1f}")

        except Exception as e:
            print(f"[!] Error processing Subject {pid}_{step}: {e}")

    classical_extractor.close()

    # Save complete dataframe
    df_res = pd.DataFrame(results)
    csv_path = os.path.join(current_dir, "results", "extractor_comparison_benchmark.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df_res.to_csv(csv_path, index=False)
    print(f"\n[OK] Saved all trial predictions to: {csv_path}")

    # Compute metrics for all 4 methods
    metrics_summary = {}
    for m in methods:
        metrics_summary[m] = compute_metrics(df_res, m)

    # Print comprehensive comparison markdown/terminal table
    print("\n" + "=" * 95)
    print("                 COMPREHENSIVE PIPELINE PERFORMANCE COMPARISON TABLE                   ")
    print("=" * 95)
    print(f"{'Metric':<32} | {'TS-CAN':<13} | {'POS (Main)':<13} | {'CHROM':<13} | {'GREEN':<13}")
    print("-" * 95)
    
    tscan_m = metrics_summary['TS-CAN']
    pos_m = metrics_summary['POS']
    chrom_m = metrics_summary['CHROM']
    green_m = metrics_summary['GREEN']

    print(f"{'SBP Mean Absolute Error (MAE)':<32} | {tscan_m['mae_sbp']:<10.2f} mmHg | {pos_m['mae_sbp']:<10.2f} mmHg | {chrom_m['mae_sbp']:<10.2f} mmHg | {green_m['mae_sbp']:<10.2f} mmHg")
    print(f"{'SBP Root Mean Square Error (RMSE)':<32} | {tscan_m['rmse_sbp']:<10.2f} mmHg | {pos_m['rmse_sbp']:<10.2f} mmHg | {chrom_m['rmse_sbp']:<10.2f} mmHg | {green_m['rmse_sbp']:<10.2f} mmHg")
    print(f"{'SBP Mean Error (Bias)':<32} | {tscan_m['bias_sbp']:<+10.2f} mmHg | {pos_m['bias_sbp']:<+10.2f} mmHg | {chrom_m['bias_sbp']:<+10.2f} mmHg | {green_m['bias_sbp']:<+10.2f} mmHg")
    print(f"{'SBP Standard Deviation (SD)':<32} | {tscan_m['sd_sbp']:<10.2f} mmHg | {pos_m['sd_sbp']:<10.2f} mmHg | {chrom_m['sd_sbp']:<10.2f} mmHg | {green_m['sd_sbp']:<10.2f} mmHg")
    print(f"{'SBP Pearson Correlation (r)':<32} | {tscan_m['r_sbp']:<+13.3f} | {pos_m['r_sbp']:<+13.3f} | {chrom_m['r_sbp']:<+13.3f} | {green_m['r_sbp']:<+13.3f}")
    print("-" * 95)
    print(f"{'DBP Mean Absolute Error (MAE)':<32} | {tscan_m['mae_dbp']:<10.2f} mmHg | {pos_m['mae_dbp']:<10.2f} mmHg | {chrom_m['mae_dbp']:<10.2f} mmHg | {green_m['mae_dbp']:<10.2f} mmHg")
    print(f"{'DBP Root Mean Square Error (RMSE)':<32} | {tscan_m['rmse_dbp']:<10.2f} mmHg | {pos_m['rmse_dbp']:<10.2f} mmHg | {chrom_m['rmse_dbp']:<10.2f} mmHg | {green_m['rmse_dbp']:<10.2f} mmHg")
    print(f"{'DBP Mean Error (Bias)':<32} | {tscan_m['bias_dbp']:<+10.2f} mmHg | {pos_m['bias_dbp']:<+10.2f} mmHg | {chrom_m['bias_dbp']:<+10.2f} mmHg | {green_m['bias_dbp']:<+10.2f} mmHg")
    print(f"{'DBP Standard Deviation (SD)':<32} | {tscan_m['sd_dbp']:<10.2f} mmHg | {pos_m['sd_dbp']:<10.2f} mmHg | {chrom_m['sd_dbp']:<10.2f} mmHg | {green_m['sd_dbp']:<10.2f} mmHg")
    print(f"{'DBP Pearson Correlation (r)':<32} | {tscan_m['r_dbp']:<+13.3f} | {pos_m['r_dbp']:<+13.3f} | {chrom_m['r_dbp']:<+13.3f} | {green_m['r_dbp']:<+13.3f}")
    print("-" * 95)
    print(f"{'Heart Rate (HR) MAE':<32} | {tscan_m['mae_hr']:<10.2f} BPM  | {pos_m['mae_hr']:<10.2f} BPM  | {chrom_m['mae_hr']:<10.2f} BPM  | {green_m['mae_hr']:<10.2f} BPM")
    print(f"{'Heart Rate (HR) Pearson (r)':<32} | {tscan_m['r_hr']:<+13.3f} | {pos_m['r_hr']:<+13.3f} | {chrom_m['r_hr']:<+13.3f} | {green_m['r_hr']:<+13.3f}")
    print("-" * 95)
    print(f"{'SBP Accuracy <= 5 mmHg':<32} | {tscan_m['pct_5_sbp']:<10.1f} %    | {pos_m['pct_5_sbp']:<10.1f} %    | {chrom_m['pct_5_sbp']:<10.1f} %    | {green_m['pct_5_sbp']:<10.1f} %")
    print(f"{'SBP Accuracy <= 10 mmHg':<32} | {tscan_m['pct_10_sbp']:<10.1f} %    | {pos_m['pct_10_sbp']:<10.1f} %    | {chrom_m['pct_10_sbp']:<10.1f} %    | {green_m['pct_10_sbp']:<10.1f} %")
    print(f"{'SBP Accuracy <= 15 mmHg':<32} | {tscan_m['pct_15_sbp']:<10.1f} %    | {pos_m['pct_15_sbp']:<10.1f} %    | {chrom_m['pct_15_sbp']:<10.1f} %    | {green_m['pct_15_sbp']:<10.1f} %")
    print("-" * 95)
    
    avg_tscan_time = np.mean(timing_data['TS-CAN']) if timing_data['TS-CAN'] else 0.0
    avg_pos_time = np.mean(timing_data['POS']) if timing_data['POS'] else 0.0
    avg_chrom_time = np.mean(timing_data['CHROM']) if timing_data['CHROM'] else 0.0
    avg_green_time = np.mean(timing_data['GREEN']) if timing_data['GREEN'] else 0.0
    
    print(f"{'Avg Processing Time / Video':<32} | {avg_tscan_time:<10.2f} s    | {avg_pos_time:<10.2f} s    | {avg_chrom_time:<10.2f} s    | {avg_green_time:<10.2f} s")
    print(f"{'Mobile / Real-time Feasibility':<32} | {'Heavy (DL)':<13} | {'Instant (DSP)':<13} | {'Instant (DSP)':<13} | {'Instant (DSP)':<13}")
    print("=" * 95)

    # Save summary plots
    fig_path = os.path.join(current_dir, "results", "extractor_benchmark_summary.png")
    generate_benchmark_summary_plots(df_res, metrics_summary, fig_path)

    # Save metrics summary table to CSV
    metrics_df = pd.DataFrame(list(metrics_summary.values()))
    summary_csv = os.path.join(current_dir, "results", "extractor_metrics_summary.csv")
    metrics_df.to_csv(summary_csv, index=False)
    print(f"[OK] Metrics summary saved to: {summary_csv}")


if __name__ == "__main__":
    run_comparative_benchmark(num_trials=16, max_sec=15.0)
