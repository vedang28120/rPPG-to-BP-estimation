import os
import pandas as pd
import numpy as np

# Determine the root directory relative to this script's location (assuming it resides in src/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, 'outputs')

def ensure_output_dir(output_dir=DEFAULT_OUTPUT_DIR):
    """
    Checks for the outputs/ folder in the root directory and creates it if it does not exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def log_pos_data(data, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Logs 13 columns of frame-by-frame data to outputs/pos_extraction_log.csv.
    Uses pandas in append mode (mode='a') to ensure efficient file writing 
    without loading the entire CSV into memory.
    
    Args:
        data: 2D NumPy array or list of lists containing exactly 13 columns:
              [Frame Index, Timestamp, Forehead R, Forehead G, Forehead B, 
               Left Cheek R, Left Cheek G, Left Cheek B, 
               Right Cheek R, Right Cheek G, Right Cheek B, 
               Raw POS Signal, Filtered BVP Signal]
        output_dir: The directory to save the CSV file.
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
    
    # Convert the raw array/list to a Pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # If the file exists, append without writing headers. Otherwise, write headers.
    file_exists = os.path.isfile(file_path)
    df.to_csv(file_path, mode='a', index=False, header=not file_exists)

def log_vitals_data(vitals_dict, output_dir=DEFAULT_OUTPUT_DIR):
    """
    Logs window-based predictions to outputs/lstm_vitals_log.csv.
    
    Args:
        vitals_dict: Dictionary containing the following exact keys:
                     ['Window ID', 'Start Time', 'End Time', 'HR', 'HRV', 'RR', 
                      'SBP', 'DBP', 'MAP', 'BP Category']
        output_dir: The directory to save the CSV file.
    """
    ensure_output_dir(output_dir)
    file_path = os.path.join(output_dir, 'lstm_vitals_log.csv')
    
    # Enforce expected column order
    columns = [
        'Window ID', 'Start Time', 'End Time', 
        'HR', 'HRV', 'RR', 
        'SBP', 'DBP', 'MAP', 'BP Category'
    ]
    
    # Convert dictionary to a single-row DataFrame
    df = pd.DataFrame([vitals_dict], columns=columns)
    
    # If the file exists, append without writing headers. Otherwise, write headers.
    file_exists = os.path.isfile(file_path)
    df.to_csv(file_path, mode='a', index=False, header=not file_exists)

if __name__ == "__main__":
    # Self-test block: Generates and logs dummy data if the script is run directly
    print("Testing data_logger module...")
    
    # 1. Test POS data logging
    print("Logging dummy POS extraction data...")
    dummy_pos_data = np.random.rand(5, 13)
    dummy_pos_data[:, 0] = np.arange(1, 6) # Frame Index
    log_pos_data(dummy_pos_data)
    
    # 2. Test Vitals data logging
    print("Logging dummy LSTM vitals prediction data...")
    dummy_vitals = {
        'Window ID': 1,
        'Start Time': 0.0,
        'End Time': 7.0,
        'HR': 72.5,
        'HRV': 45.2,
        'RR': 16,
        'SBP': 120.0,
        'DBP': 80.0,
        'MAP': 93.3,
        'BP Category': 'Normal'
    }
    log_vitals_data(dummy_vitals)
    
    print(f"Test complete. Logs have been written to: {DEFAULT_OUTPUT_DIR}")
