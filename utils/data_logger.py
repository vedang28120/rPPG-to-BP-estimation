"""
Telemetry & Data Logger Module
Provides high-performance append-mode CSV logging for frame-by-frame rPPG traces and windowed vitals.
"""

import os
import pandas as pd
import numpy as np

# Repo root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, 'data', 'processed')

def ensure_output_dir(output_dir=DEFAULT_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def log_pos_data(data, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Logs 13 columns of frame-by-frame data to data/processed/pos_extraction_log.csv.
    """
    ensure_output_dir(output_dir)
    file_path = os.path.join(output_dir, 'pos_extraction_log.csv')
    
    columns = [
        'Frame Index', 'Timestamp', 
        'Forehead R', 'Forehead G', 'Forehead B',
        'Left Cheek R', 'Left Cheek G', 'Left Cheek B',
        'Right Cheek R', 'Right Cheek G', 'Right Cheek B',
        'Raw POS Signal', 'Filtered BVP Signal'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    file_exists = os.path.isfile(file_path)
    df.to_csv(file_path, mode='a', index=False, header=not file_exists)

def log_vitals_data(vitals_dict, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Logs window-based predictions to data/processed/vitals_log.csv.
    """
    ensure_output_dir(output_dir)
    file_path = os.path.join(output_dir, 'vitals_log.csv')
    
    columns = [
        'Window ID', 'Start Time', 'End Time', 
        'HR', 'HRV', 'RR', 
        'SBP', 'DBP', 'MAP', 'BP Category'
    ]
    
    df = pd.DataFrame([vitals_dict], columns=columns)
    file_exists = os.path.isfile(file_path)
    df.to_csv(file_path, mode='a', index=False, header=not file_exists)
