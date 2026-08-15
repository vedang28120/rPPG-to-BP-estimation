import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def generate_mae_boxplot(output_path="mae_boxplot.png"):
    """
    Generates a seaborn boxplot showing the Mean Absolute Error (MAE) 
    for Heart Rate (bpm) and Blood Pressure (mmHg) across different 
    simulated testing conditions (e.g., 'Steady', 'Talking', 'Movement').
    """
    # 1. Simulate MAE data for 30 subjects across 3 conditions
    np.random.seed(42)
    n_subjects = 30
    
    conditions = ['Steady', 'Talking', 'Movement']
    
    # Base MAE values
    base_hr_mae = {'Steady': 1.5, 'Talking': 3.0, 'Movement': 6.5}
    base_sbp_mae = {'Steady': 4.0, 'Talking': 7.0, 'Movement': 12.0}
    base_dbp_mae = {'Steady': 2.5, 'Talking': 5.0, 'Movement': 8.5}
    
    data = []
    
    for condition in conditions:
        hr_mae = np.random.normal(loc=base_hr_mae[condition], scale=1.0, size=n_subjects)
        sbp_mae = np.random.normal(loc=base_sbp_mae[condition], scale=1.5, size=n_subjects)
        dbp_mae = np.random.normal(loc=base_dbp_mae[condition], scale=1.2, size=n_subjects)
        
        # Ensure non-negative MAE
        hr_mae = np.clip(hr_mae, 0.1, None)
        sbp_mae = np.clip(sbp_mae, 0.5, None)
        dbp_mae = np.clip(dbp_mae, 0.5, None)
        
        for i in range(n_subjects):
            data.append({'Condition': condition, 'Metric': 'HR (bpm)', 'MAE': hr_mae[i]})
            data.append({'Condition': condition, 'Metric': 'SBP (mmHg)', 'MAE': sbp_mae[i]})
            data.append({'Condition': condition, 'Metric': 'DBP (mmHg)', 'MAE': dbp_mae[i]})
            
    df = pd.DataFrame(data)
    
    # 2. Plotting with Seaborn
    sns.set_theme(style="whitegrid", context="paper")
    plt.figure(figsize=(10, 6))
    
    ax = sns.boxplot(x="Condition", y="MAE", hue="Metric", data=df, palette="Set2")
    
    # Aesthetics
    plt.title("Mean Absolute Error (MAE) Across Testing Conditions", fontsize=14)
    plt.ylabel("Mean Absolute Error", fontsize=12)
    plt.xlabel("Testing Condition", fontsize=12)
    
    # Place legend appropriately
    plt.legend(title='Vital Sign', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Saved MAE boxplot to {output_path}")

if __name__ == "__main__":
    generate_mae_boxplot("mae_boxplot.png")
