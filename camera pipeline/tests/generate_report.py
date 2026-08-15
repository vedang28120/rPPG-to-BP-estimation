import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

csv_path = r'c:/Users/simpl/.antigravity-ide/Projects/rPPG to BP estimation/camera pipeline/tests/mcd_50subjects_benchmark.csv'
out_dir = r'c:/Users/simpl/.antigravity-ide/Projects/rPPG to BP estimation/camera pipeline/tests'

df = pd.read_csv(csv_path)

mae_sbp = np.mean(df['sbp_err'])
rmse_sbp = np.sqrt(np.mean((df['pred_sbp'] - df['actual_sbp'])**2))
r_sbp = np.corrcoef(df['actual_sbp'], df['pred_sbp'])[0, 1]

mae_dbp = np.mean(df['dbp_err'])
rmse_dbp = np.sqrt(np.mean((df['pred_dbp'] - df['actual_dbp'])**2))
r_dbp = np.corrcoef(df['actual_dbp'], df['pred_dbp'])[0, 1]

valid_hr = df[df['actual_hr'] > 0]
mae_hr = np.mean(valid_hr['hr_err']) if len(valid_hr) > 0 else 0.0

md_path = os.path.join(out_dir, 'accuracy_report_50subjects.md')
with open(md_path, 'w', encoding='utf-8') as f:
    f.write('# MCD Dataset 50-Subject Comprehensive Model Benchmark Report\n\n')
    f.write(f'Evaluated **{len(df)} trials across 50 MCD dataset subjects** against clinical blood pressure measurements.\n\n')
    f.write('### 📊 Statistical Performance Summary\n\n')
    f.write('| Vital Metric | MAE (Mean Abs Error) | RMSE (Root Mean Sq Error) | Pearson Correlation (r) |\n')
    f.write('|---|---|---|---|\n')
    f.write(f'| **Systolic BP (SBP)** | **`{mae_sbp:.2f} mmHg`** | `{rmse_sbp:.2f} mmHg` | `{r_sbp:.3f}` |\n')
    f.write(f'| **Diastolic BP (DBP)** | **`{mae_dbp:.2f} mmHg`** | `{rmse_dbp:.2f} mmHg` | `{r_dbp:.3f}` |\n')
    f.write(f'| **Heart Rate (HR)** | **`{mae_hr:.2f} BPM`** | - | - |\n\n')
    
    f.write('### 📋 Complete 50-Subject Breakdown\n\n')
    f.write('| Subject ID | Trial | Actual SBP | Pred SBP | SBP Err | Actual DBP | Pred DBP | DBP Err | Actual MAP | Pred MAP |\n')
    f.write('|---|---|---|---|---|---|---|---|---|---|\n')
    for idx, r in df.iterrows():
        f.write(f"| {int(r['subject_id'])} | {r['step']} | {r['actual_sbp']} | {r['pred_sbp']} | {r['sbp_err']} | {r['actual_dbp']} | {r['pred_dbp']} | {r['dbp_err']} | {r['actual_map']} | {r['pred_map']} |\n")

# Generate Plots
fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# SBP Scatter
axes[0, 0].scatter(df['actual_sbp'], df['pred_sbp'], alpha=0.7, color='#9C27B0', edgecolors='k')
axes[0, 0].plot([80, 160], [80, 160], 'r--', label='Ideal 1:1')
axes[0, 0].set_xlabel('Actual Systolic BP (mmHg)')
axes[0, 0].set_ylabel('Predicted Systolic BP (mmHg)')
axes[0, 0].set_title(f'SBP Prediction vs Actual (MAE={mae_sbp:.2f} mmHg)')
axes[0, 0].legend()
axes[0, 0].grid(True, linestyle='--', alpha=0.5)

# DBP Scatter
axes[0, 1].scatter(df['actual_dbp'], df['pred_dbp'], alpha=0.7, color='#2196F3', edgecolors='k')
axes[0, 1].plot([50, 110], [50, 110], 'r--', label='Ideal 1:1')
axes[0, 1].set_xlabel('Actual Diastolic BP (mmHg)')
axes[0, 1].set_ylabel('Predicted Diastolic BP (mmHg)')
axes[0, 1].set_title(f'DBP Prediction vs Actual (MAE={mae_dbp:.2f} mmHg)')
axes[0, 1].legend()
axes[0, 1].grid(True, linestyle='--', alpha=0.5)

# Bland-Altman SBP
mean_sbp = (df['actual_sbp'] + df['pred_sbp']) / 2.0
diff_sbp = df['pred_sbp'] - df['actual_sbp']
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
mean_dbp = (df['actual_dbp'] + df['pred_dbp']) / 2.0
diff_dbp = df['pred_dbp'] - df['actual_dbp']
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
plot_path = os.path.join(out_dir, 'bland_altman_50subjects.png')
plt.savefig(plot_path, dpi=300)
plt.close()

print('SUMMARY STATS:')
print(f'  - SBP MAE: {mae_sbp:.2f} mmHg (RMSE: {rmse_sbp:.2f}, r={r_sbp:.3f})')
print(f'  - DBP MAE: {mae_dbp:.2f} mmHg (RMSE: {rmse_dbp:.2f}, r={r_dbp:.3f})')
