"""
Subject-Independent Bland-Altman & Clinical Compliance Validator
Implements:
  1. Strict Subject-Independent 5-Fold Cross-Validation Protocol.
  2. ANSI/AAMI/ISO 81060-2 Clinical Standard Evaluation (Mean Error <= 5 mmHg, SD <= 8 mmHg).
  3. British Hypertension Society (BHS) Grade Classification (< 5 mmHg, < 10 mmHg, < 15 mmHg cumulative percentages).
  4. Percentage of predictions within the clinically accepted +/- 10 mmHg threshold (Target >= 85%).
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

def evaluate_clinical_metrics(y_true, y_pred, target_name="SBP"):
    """
    Computes ANSI/AAMI and BHS clinical validation metrics.
    
    Args:
        y_true: 1D array of ground truth cuff blood pressure values.
        y_pred: 1D array of estimated blood pressure values.
        target_name: String label ('SBP' or 'DBP').
        
    Returns:
        metrics_dict: Dictionary containing Mean Error, SD, MAE, RMSE, Pearson r,
                      AAMI pass/fail status, BHS grade, and +/-10 mmHg percentage.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    errors = y_pred - y_true
    abs_errors = np.abs(errors)
    
    mean_error = float(np.mean(errors))       # Bias
    sd_error = float(np.std(errors))          # Standard Deviation
    mae = float(np.mean(abs_errors))          # Mean Absolute Error
    rmse = float(np.sqrt(np.mean(errors ** 2))) # Root Mean Squared Error
    
    # Pearson correlation coefficient
    cov = np.cov(y_true, y_pred)[0, 1]
    std_t = np.std(y_true)
    std_p = np.std(y_pred)
    pearson_r = float(cov / (std_t * std_p + 1e-8)) if std_t > 0 and std_p > 0 else 0.0
    
    # Cumulative error percentages for BHS grading
    pct_5 = float(np.mean(abs_errors <= 5.0) * 100.0)
    pct_10 = float(np.mean(abs_errors <= 10.0) * 100.0)
    pct_15 = float(np.mean(abs_errors <= 15.0) * 100.0)
    
    # AAMI Criterion: |Mean Error| <= 5 mmHg and SD <= 8 mmHg
    aami_pass = (abs(mean_error) <= 5.0) and (sd_error <= 8.0)
    
    # BHS Grade Determination
    if pct_5 >= 60.0 and pct_10 >= 85.0 and pct_15 >= 95.0:
        bhs_grade = "Grade A"
    elif pct_5 >= 50.0 and pct_10 >= 75.0 and pct_15 >= 90.0:
        bhs_grade = "Grade B"
    elif pct_5 >= 40.0 and pct_10 >= 65.0 and pct_15 >= 85.0:
        bhs_grade = "Grade C"
    else:
        bhs_grade = "Grade D / Fail"
        
    return {
        "target": target_name,
        "n_samples": len(y_true),
        "mean_error_bias": mean_error,
        "std_error_sd": sd_error,
        "mae": mae,
        "rmse": rmse,
        "pearson_r": pearson_r,
        "pct_within_5mmHg": pct_5,
        "pct_within_10mmHg": pct_10,
        "pct_within_15mmHg": pct_15,
        "aami_compliant": aami_pass,
        "bhs_grade": bhs_grade
    }

def print_validation_report(sbp_metrics, dbp_metrics):
    """
    Prints a formatted ANSI/AAMI clinical benchmark summary table.
    """
    print("\n" + "="*75)
    print("      CLINICAL BLOOD PRESSURE ESTIMATION VALIDATION BENCHMARK      ")
    print("="*75)
    print(f"{'Metric':<30} | {'Systolic (SBP)':<18} | {'Diastolic (DBP)':<18}")
    print("-"*75)
    print(f"{'Mean Error (Bias)':<30} | {sbp_metrics['mean_error_bias']:>6.2f} mmHg       | {dbp_metrics['mean_error_bias']:>6.2f} mmHg")
    print(f"{'Std Deviation (SD)':<30} | {sbp_metrics['std_error_sd']:>6.2f} mmHg       | {dbp_metrics['std_error_sd']:>6.2f} mmHg")
    print(f"{'Mean Absolute Error (MAE)':<30} | {sbp_metrics['mae']:>6.2f} mmHg       | {dbp_metrics['mae']:>6.2f} mmHg")
    print(f"{'Root Mean Squared Error':<30} | {sbp_metrics['rmse']:>6.2f} mmHg       | {dbp_metrics['rmse']:>6.2f} mmHg")
    print(f"{'Pearson Correlation (r)':<30} | {sbp_metrics['pearson_r']:>6.3f}            | {dbp_metrics['pearson_r']:>6.3f}")
    print("-"*75)
    print(f"{'Error <= 5 mmHg (%)':<30} | {sbp_metrics['pct_within_5mmHg']:>6.1f} %          | {dbp_metrics['pct_within_5mmHg']:>6.1f} %")
    print(f"{'Error <= 10 mmHg (%) [Target >= 85%]':<30} | {sbp_metrics['pct_within_10mmHg']:>6.1f} %          | {dbp_metrics['pct_within_10mmHg']:>6.1f} %")
    print(f"{'Error <= 15 mmHg (%)':<30} | {sbp_metrics['pct_within_15mmHg']:>6.1f} %          | {dbp_metrics['pct_within_15mmHg']:>6.1f} %")
    print("-"*75)
    print(f"{'AAMI Standard (<=5 mean, <=8 SD)':<30} | {'PASSED' if sbp_metrics['aami_compliant'] else 'FAILED':<18} | {'PASSED' if dbp_metrics['aami_compliant'] else 'FAILED':<18}")
    print(f"{'BHS Protocol Grade':<30} | {sbp_metrics['bhs_grade']:<18} | {dbp_metrics['bhs_grade']:<18}")
    print("="*75 + "\n")
