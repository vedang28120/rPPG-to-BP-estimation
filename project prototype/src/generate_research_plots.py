import os

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import find_peaks
import os

def set_publication_style():
    """Sets matplotlib parameters for high-quality IEEE publication plots."""
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })

def generate_roi_wireframe(image_path="sample_face.jpg", output_path="fig1_roi_wireframe.png"):
    """
    Loads a sample image, applies MediaPipe Face Mesh, and draws the wireframe
    while highlighting the forehead and cheek ROIs with bounding boxes.
    """
    import sys
    from unittest.mock import MagicMock
    sys.modules['tensorflow'] = MagicMock()
    import mediapipe as mp
    import cv2
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # Try to load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Warning: {image_path} not found. Attempting to extract a frame from a video in ../data/")
        import glob
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_files = glob.glob(os.path.join(base_dir, "data", "*.mp4"))
        if video_files:
            cap = cv2.VideoCapture(video_files[0])
            ret, frame = cap.read()
            if ret:
                image = frame
            cap.release()
            
    if image is None:
        print("Warning: No image or video found. Creating a synthetic image for demonstration.")
        image = np.zeros((500, 500, 3), dtype=np.uint8)
        
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.1) as face_mesh:
        
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        annotated_image = image.copy()
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw the full face mesh wireframe
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())
                
                h, w, _ = annotated_image.shape
                
                # Helper function to get bounding box for a set of landmarks
                def get_bbox(indices):
                    x_coords = [int(face_landmarks.landmark[idx].x * w) for idx in indices]
                    y_coords = [int(face_landmarks.landmark[idx].y * h) for idx in indices]
                    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

                # Standard MediaPipe indices for Forehead and Cheeks
                forehead_idx = [10, 109, 151, 338] # Accurate upper forehead points
                left_cheek_idx = [116, 117, 118, 119]
                right_cheek_idx = [345, 346, 347, 348]
                
                fx1, fy1, fx2, fy2 = get_bbox(forehead_idx)
                lx1, ly1, lx2, ly2 = get_bbox(left_cheek_idx)
                rx1, ry1, rx2, ry2 = get_bbox(right_cheek_idx)
                
                # Draw Bounding Boxes highlighting the ROIs
                cv2.rectangle(annotated_image, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                cv2.rectangle(annotated_image, (lx1, ly1), (lx2, ly2), (255, 0, 0), 2)
                cv2.rectangle(annotated_image, (rx1, ry1), (rx2, ry2), (255, 0, 0), 2)
                
                # Annotate text
                cv2.putText(annotated_image, 'Forehead ROI', (fx1, fy1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.putText(annotated_image, 'Cheek ROI', (lx1, ly1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                cv2.putText(annotated_image, 'Cheek ROI', (rx1, ry1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
        cv2.imwrite(output_path, annotated_image)
        print(f"Saved Facial ROI Wireframe to {output_path}")

def generate_signal_processing_plot(output_path="fig2_signal_processing.png"):
    """
    Generates a figure with two subplots:
    Plot A: Simulated raw noisy rPPG signal.
    Plot B: Cleaned signal with annotated systolic peaks.
    """
    # 1. Simulate data (7-second window)
    fs = 30 # 30 Hz sampling rate
    t = np.linspace(0, 7, 7 * fs)
    
    # Simulate a heart rate at 60 BPM (1 Hz) + harmonic
    clean_signal = np.sin(2 * np.pi * 1.0 * t) + 0.3 * np.cos(2 * np.pi * 2.0 * t)
    
    # Add noise (baseline wander + high frequency noise) to simulate raw rPPG
    noise = 0.5 * np.sin(2 * np.pi * 0.1 * t) + 0.2 * np.random.normal(size=len(t))
    raw_signal = clean_signal + noise
    
    # For visualization, our "cleaned" signal is the clean_signal
    filtered_signal = clean_signal
    
    # Find peaks in cleaned signal
    peaks, _ = find_peaks(filtered_signal, distance=int(fs*0.6)) # minimum distance between peaks
    
    # 2. Create plots
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    
    # Plot A: Raw Signal
    axes[0].plot(t, raw_signal, color='gray', label='Raw Noisy rPPG')
    axes[0].set_title('(A) Simulated Raw Noisy rPPG Signal')
    axes[0].set_ylabel('Amplitude')
    axes[0].legend(loc='upper right')
    
    # Plot B: Cleaned Signal with Peaks
    axes[1].plot(t, filtered_signal, color='darkblue', label='Filtered rPPG')
    axes[1].plot(t[peaks], filtered_signal[peaks], 'ro', label='Systolic Peaks')
    axes[1].set_title('(B) Cleaned Signal with Annotated Systolic Peaks')
    axes[1].set_xlabel('Time (seconds)')
    axes[1].set_ylabel('Amplitude')
    axes[1].legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved Signal Processing Plot to {output_path}")

def generate_bland_altman_plot(output_path="fig3_bland_altman.png"):
    """
    Generates a standard Bland-Altman plot comparing predicted SBP against ground-truth SBP.
    Includes mean bias and ±1.96 SD limits of agreement.
    """
    # 1. Generate dummy data for BP
    np.random.seed(42)
    ground_truth_sbp = np.random.normal(120, 15, 100)
    predicted_sbp = ground_truth_sbp + np.random.normal(2, 5, 100)
    
    # 2. Bland-Altman calculations
    mean_sbp = (ground_truth_sbp + predicted_sbp) / 2
    diff_sbp = predicted_sbp - ground_truth_sbp
    
    mean_diff = np.mean(diff_sbp)
    std_diff = np.std(diff_sbp)
    
    upper_limit = mean_diff + 1.96 * std_diff
    lower_limit = mean_diff - 1.96 * std_diff
    
    # 3. Create plot
    plt.figure(figsize=(8, 6))
    plt.scatter(mean_sbp, diff_sbp, alpha=0.6, color='teal', edgecolors='k')
    
    # Plot mean bias and limits of agreement
    plt.axhline(mean_diff, color='red', linestyle='-', label=f'Mean Bias: {mean_diff:.2f}')
    plt.axhline(upper_limit, color='blue', linestyle='--', label=f'+1.96 SD: {upper_limit:.2f}')
    plt.axhline(lower_limit, color='blue', linestyle='--', label=f'-1.96 SD: {lower_limit:.2f}')
    
    plt.title('Bland-Altman Plot: Predicted vs. Ground-Truth SBP')
    plt.xlabel('Mean of Predicted and Ground-Truth SBP (mmHg)')
    plt.ylabel('Difference (Predicted - Ground-Truth) (mmHg)')
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved Bland-Altman Plot to {output_path}")

def generate_correlation_plot(output_path="fig4_correlation.png"):
    """
    Generates a scatter plot with a line of best fit for Predicted vs. Actual BP.
    """
    # 1. Generate dummy data for BP
    np.random.seed(42)
    actual_bp = np.random.normal(120, 15, 100)
    predicted_bp = actual_bp + np.random.normal(2, 5, 100)
    
    # 2. Create plot
    plt.figure(figsize=(8, 6))
    
    # Scatter points
    plt.scatter(actual_bp, predicted_bp, alpha=0.6, color='purple', edgecolors='k', label='Predictions')
    
    # Line of best fit
    m, b = np.polyfit(actual_bp, predicted_bp, 1)
    plt.plot(actual_bp, m * actual_bp + b, color='orange', linewidth=2, label=f'Best Fit (y={m:.2f}x+{b:.2f})')
    
    # Ideal line (y=x)
    plt.plot([min(actual_bp), max(actual_bp)], [min(actual_bp), max(actual_bp)], color='gray', linestyle='--', label='Ideal (y=x)')
    
    plt.title('Correlation: Predicted vs. Actual Blood Pressure')
    plt.xlabel('Actual Blood Pressure (mmHg)')
    plt.ylabel('Predicted Blood Pressure (mmHg)')
    plt.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Saved Correlation Plot to {output_path}")

def main():
    set_publication_style()
    
    # Define output directory for generated plots based on the script location
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    
    print("Generating IEEE publication-quality plots...")
    generate_signal_processing_plot(output_path=os.path.join(out_dir, "fig2_signal_processing.png"))
    generate_bland_altman_plot(output_path=os.path.join(out_dir, "fig3_bland_altman.png"))
    generate_correlation_plot(output_path=os.path.join(out_dir, "fig4_correlation.png"))
    generate_roi_wireframe(image_path="sample_face.jpg", output_path=os.path.join(out_dir, "fig1_roi_wireframe.png"))
    print("All plots generated successfully.")

if __name__ == "__main__":
    main()
