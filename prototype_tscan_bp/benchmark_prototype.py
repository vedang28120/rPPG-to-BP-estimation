"""
Batch Benchmark Script for TS-CAN + MODEL-06 Prototype Pipeline
Evaluates multiple MCD-rPPG video trials against clinical ground truth.
"""
import os
import sys
import pandas as pd
import numpy as np
from huggingface_hub import hf_hub_download

# Add root directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from prototype_tscan_bp.download_weights import setup_all_checkpoints
from prototype_tscan_bp.tscan_extractor import TSCANExtractor
from prototype_tscan_bp.bp_estimator import BPEstimationEngine

def run_benchmark(num_trials=15, max_sec=15.0):
    print("=" * 75)
    print(f"      EVALUATING TS-CAN + MODEL-06 PIPELINE ON {num_trials} MCD TRIALS      ")
    print("=" * 75)

    db_path = hf_hub_download('wengziheng/mcd_rppg', 'db.csv', repo_type='dataset')
    df = pd.read_csv(db_path)
    df_valid = df[(df['upper_ap'].notnull()) & (df['lower_ap'].notnull())].drop_duplicates(subset=['patient_id', 'step']).copy()

    tscan_ckpt, bp_ckpt = setup_all_checkpoints()
    extractor = TSCANExtractor(checkpoint_path=tscan_ckpt, device='cpu')
    bp_engine = BPEstimationEngine(checkpoint_path=bp_ckpt, device='cpu')

    mcd_dir = r"E:\VT\PPG rPPG BP project\MCD_rppg"
    results = []
    processed = 0

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
            
        try:
            pulse, fps, bpm, _ = extractor.process_video(vid_path, max_duration_sec=max_sec)
            age = float(row['age']) if not np.isnan(row['age']) else 25.0
            gender = 1 if row['sex'] == 'M' else 0
            bmi = float(row['bmi']) if not np.isnan(row['bmi']) else 22.0
            
            pred = bp_engine.predict_bp(pulse, source_fs=fps, age=age, gender=gender, bmi=bmi)
            gt_sbp = float(row['upper_ap'])
            gt_dbp = float(row['lower_ap'])
            gt_hr = float(row['pulse']) if not np.isnan(row['pulse']) else None
            
            sbp_err = abs(pred['sbp'] - gt_sbp)
            dbp_err = abs(pred['dbp'] - gt_dbp)
            
            results.append({
                'subject_id': pid,
                'step': step,
                'age': age,
                'gender': 'M' if gender == 1 else 'F',
                'bmi': round(bmi, 1),
                'gt_sbp': gt_sbp,
                'pred_sbp': pred['sbp'],
                'sbp_err': round(sbp_err, 1),
                'gt_dbp': gt_dbp,
                'pred_dbp': pred['dbp'],
                'dbp_err': round(dbp_err, 1),
                'gt_hr': gt_hr,
                'pred_hr': round(bpm, 1)
            })
            processed += 1
            print(f"[{processed:02d}/{num_trials}] Subject {pid} ({step:<6}): SBP Pred={pred['sbp']:.1f} (GT={gt_sbp:.1f}, Err={sbp_err:.1f}) | DBP Pred={pred['dbp']:.1f} (GT={gt_dbp:.1f}, Err={dbp_err:.1f})")
        except Exception as e:
            print(f"[!] Error processing Subject {pid}_{step}: {e}")

    df_res = pd.DataFrame(results)
    csv_path = os.path.join(current_dir, "results", "prototype_batch_benchmark.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df_res.to_csv(csv_path, index=False)

    # Compute aggregate metrics
    mae_sbp = float(df_res['sbp_err'].mean())
    rmse_sbp = float(np.sqrt(np.mean((df_res['pred_sbp'] - df_res['gt_sbp'])**2)))
    r_sbp = float(np.corrcoef(df_res['gt_sbp'], df_res['pred_sbp'])[0, 1]) if len(df_res) > 1 else 0.0

    mae_dbp = float(df_res['dbp_err'].mean())
    rmse_dbp = float(np.sqrt(np.mean((df_res['pred_dbp'] - df_res['gt_dbp'])**2)))
    r_dbp = float(np.corrcoef(df_res['gt_dbp'], df_res['pred_dbp'])[0, 1]) if len(df_res) > 1 else 0.0

    bias_sbp = float(np.mean(df_res['pred_sbp'] - df_res['gt_sbp']))
    sd_sbp = float(np.std(df_res['pred_sbp'] - df_res['gt_sbp']))

    bias_dbp = float(np.mean(df_res['pred_dbp'] - df_res['gt_dbp']))
    sd_dbp = float(np.std(df_res['pred_dbp'] - df_res['gt_dbp']))

    pct_5_sbp = float(np.mean(df_res['sbp_err'] <= 5.0) * 100.0)
    pct_10_sbp = float(np.mean(df_res['sbp_err'] <= 10.0) * 100.0)
    pct_15_sbp = float(np.mean(df_res['sbp_err'] <= 15.0) * 100.0)

    pct_5_dbp = float(np.mean(df_res['dbp_err'] <= 5.0) * 100.0)
    pct_10_dbp = float(np.mean(df_res['dbp_err'] <= 10.0) * 100.0)
    pct_15_dbp = float(np.mean(df_res['dbp_err'] <= 15.0) * 100.0)

    print("\n" + "=" * 75)
    print("                    AGGREGATE PIPELINE PERFORMANCE                    ")
    print("=" * 75)
    print(f"{'Metric':<30} | {'Systolic BP (SBP)':<20} | {'Diastolic BP (DBP)':<20}")
    print("-" * 75)
    print(f"{'Mean Absolute Error (MAE)':<30} | {f'{mae_sbp:.2f} mmHg':<20} | {f'{mae_dbp:.2f} mmHg':<20}")
    print(f"{'Root Mean Square Error (RMSE)':<30} | {f'{rmse_sbp:.2f} mmHg':<20} | {f'{rmse_dbp:.2f} mmHg':<20}")
    print(f"{'Mean Error (Bias)':<30} | {f'{bias_sbp:+.2f} mmHg':<20} | {f'{bias_dbp:+.2f} mmHg':<20}")
    print(f"{'Standard Deviation (SD)':<30} | {f'{sd_sbp:.2f} mmHg':<20} | {f'{sd_dbp:.2f} mmHg':<20}")
    print(f"{'Pearson Correlation (r)':<30} | {f'{r_sbp:+.3f}':<20} | {f'{r_dbp:+.3f}':<20}")
    print(f"{'Accuracy <= 5 mmHg':<30} | {f'{pct_5_sbp:.1f}%':<20} | {f'{pct_5_dbp:.1f}%':<20}")
    print(f"{'Accuracy <= 10 mmHg':<30} | {f'{pct_10_sbp:.1f}%':<20} | {f'{pct_10_dbp:.1f}%':<20}")
    print(f"{'Accuracy <= 15 mmHg':<30} | {f'{pct_15_sbp:.1f}%':<20} | {f'{pct_15_dbp:.1f}%':<20}")
    print(f"{'ISO/AAMI Compliance':<30} | {('PASS' if abs(bias_sbp)<=5 and sd_sbp<=8 else 'FAIL'):<20} | {('PASS' if abs(bias_dbp)<=5 and sd_dbp<=8 else 'FAIL'):<20}")
    print("=" * 75)

if __name__ == "__main__":
    run_benchmark(num_trials=12, max_sec=12.0)
