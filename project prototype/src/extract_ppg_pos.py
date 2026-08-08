import cv2

import sys
import types
dummy = types.ModuleType('runtime_version')
dummy.Domain = type('Domain', (), {'PUBLIC': 1})
dummy.ValidateProtobufRuntimeVersion = lambda *args, **kwargs: None
sys.modules['google.protobuf.runtime_version'] = dummy
import google.protobuf
google.protobuf.runtime_version = dummy

import mediapipe as mp
import numpy as np
from scipy import signal
from scipy.interpolate import CubicSpline
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys
import os

def extract_rois(frame, landmarks, w, h):
    """
    Extracts spatial mean of RGB values for Forehead and Cheeks ROIs.
    """
    # MediaPipe landmarks for ROIs
    # To keep it simple and robust, we use bounding boxes around key points
    
    # Forehead keypoints: 10 (top), 9 (bottom), 67 (left), 297 (right)
    # Left cheek: 116, 117, 118, 119
    # Right cheek: 345, 346, 347, 348
    
    def get_bbox(indices):
        xs = [int(landmarks.landmark[i].x * w) for i in indices]
        ys = [int(landmarks.landmark[i].y * h) for i in indices]
        x_min, x_max = max(0, min(xs)), min(w, max(xs))
        y_min, y_max = max(0, min(ys)), min(h, max(ys))
        return x_min, x_max, y_min, y_max

    rois = {
        'forehead': get_bbox([10, 109, 151, 338]), # Accurate upper forehead points
        'left_cheek': get_bbox([116, 117, 118, 119]),
        'right_cheek': get_bbox([345, 346, 347, 348])
    }

    rgb_means = []
    roi_boxes = []

    for name, (x_min, x_max, y_min, y_max) in rois.items():
        if x_max > x_min and y_max > y_min:
            patch = frame[y_min:y_max, x_min:x_max]
            # Mean RGB
            r = np.mean(patch[:, :, 0])
            g = np.mean(patch[:, :, 1])
            b = np.mean(patch[:, :, 2])
            rgb_means.append([r, g, b])
            roi_boxes.append((x_min, y_min, x_max, y_max))

    # Average across all 3 ROIs
    if len(rgb_means) > 0:
        mean_rgb = np.mean(rgb_means, axis=0)
    else:
        mean_rgb = np.array([0.0, 0.0, 0.0])

    return mean_rgb, roi_boxes

def pos_algorithm(rgb_signal, fps, window_size=1.6):
    """
    Implements the Plane-Orthogonal-to-Skin (POS) algorithm (Wang et al., 2016).
    """
    l = int(fps * window_size)
    n = len(rgb_signal)
    
    # Initialize the output signal and overlap-add buffer
    h = np.zeros(n)
    
    for i in range(n - l + 1):
        # 1. Temporal Windowing
        C = rgb_signal[i:i+l]
        
        # 2. Normalization
        mean_C = np.mean(C, axis=0)
        # Avoid division by zero
        mean_C[mean_C == 0] = 1e-5
        C_norm = C / mean_C
        
        # 3. Projection
        # C_norm is shape (L, 3), containing [R, G, B]
        R = C_norm[:, 0]
        G = C_norm[:, 1]
        B = C_norm[:, 2]
        
        # X = 3G - 2B
        X = 3 * G - 2 * B
        
        # Y = 1.5R + G - 1.5B
        Y = 1.5 * R + G - 1.5 * B
        
        # 4. Tuning
        std_X = np.std(X)
        std_Y = np.std(Y)
        alpha = std_X / std_Y if std_Y != 0 else 0
        
        S = X + alpha * Y
        
        # 5. Overlap-Add
        h[i:i+l] += S - np.mean(S)
        
    return h

def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    4th-order Butterworth Bandpass Filter.
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.filtfilt(b, a, data)
    return y

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description='POS PPG Extraction Pipeline')
    parser.add_argument('--video', type=str, default=os.path.join(base_dir, 'data', 'WIN_20260731_09_47_27_Pro.mp4'), help='Input video file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (exports debug_roi.mp4)')
    args = parser.parse_args()

    video_path = args.video
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found.")
        sys.exit(1)

    print(f"Opening video: {video_path}")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video Info: {w}x{h} @ {fps:.2f} FPS | {total_frames} frames")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    rgb_trace = []
    
    if args.debug:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_video = cv2.VideoWriter(os.path.join(base_dir, 'results', 'debug_roi.mp4'), fourcc, fps, (w, h))

    print("Extracting ROI RGB values...")
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = face_mesh.process(frame_rgb)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            mean_rgb, roi_boxes = extract_rois(frame_rgb, landmarks, w, h)
            rgb_trace.append(mean_rgb)
            
            if args.debug:
                debug_frame = frame.copy()
                for (x_min, y_min, x_max, y_max) in roi_boxes:
                    cv2.rectangle(debug_frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                out_video.write(debug_frame)
        else:
            # If face lost, append previous or zeros
            if len(rgb_trace) > 0:
                rgb_trace.append(rgb_trace[-1])
            else:
                rgb_trace.append([0.0, 0.0, 0.0])
                
            if args.debug:
                out_video.write(frame)
                
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"Processed {frame_count}/{total_frames} frames...")

    cap.release()
    if args.debug:
        out_video.release()
        print("Saved debug video to " + os.path.join(base_dir, 'results', 'debug_roi.mp4'))
        
    rgb_trace = np.array(rgb_trace)
    
    print("Running POS Algorithm...")
    raw_pos = pos_algorithm(rgb_trace, fps)
    
    print("Resampling to 125 Hz via Cubic Spline Interpolation...")
    original_time_axis = np.arange(len(raw_pos)) / fps
    new_fps = 125.0
    time_axis_125 = np.arange(0, original_time_axis[-1], 1.0 / new_fps)
    cs = CubicSpline(original_time_axis, raw_pos)
    raw_pos_125 = cs(time_axis_125)
    
    print("Filtering and Normalizing Signal...")
    filtered_pos = butter_bandpass_filter(raw_pos_125, 0.75, 4.0, new_fps, order=4)
    
    # Z-score normalization
    normalized_pos = (filtered_pos - np.mean(filtered_pos)) / (np.std(filtered_pos) + 1e-8)
    
    print("Saving Outputs...")
    # Export to CSV and NPY
    df = pd.DataFrame({'time_sec': time_axis_125, 'ppg_normalized': normalized_pos})
    df.to_csv(os.path.join(base_dir, 'data', 'ppg_output.csv'), index=False)
    np.save(os.path.join(base_dir, 'data', 'ppg_output.npy'), normalized_pos)
    
    # Data Visualization
    plt.figure(figsize=(12, 10))
    
    plt.subplot(3, 1, 1)
    plt.title('Raw Spatial Mean RGB Trace')
    plt.plot(original_time_axis, rgb_trace[:, 0], 'r', label='Red')
    plt.plot(original_time_axis, rgb_trace[:, 1], 'g', label='Green')
    plt.plot(original_time_axis, rgb_trace[:, 2], 'b', label='Blue')
    plt.legend()
    plt.ylabel('Pixel Value')
    
    plt.subplot(3, 1, 2)
    plt.title('Raw POS Projected Signal')
    plt.plot(original_time_axis, raw_pos, 'k')
    plt.ylabel('Amplitude')
    
    plt.subplot(3, 1, 3)
    plt.title('Filtered & Normalized BVP Waveform (125 Hz)')
    plt.plot(time_axis_125, normalized_pos, 'm')
    plt.xlabel('Time (s)')
    plt.ylabel('Normalized Amplitude')
    
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, 'results', 'ppg_visualization_report.png'))
    print("Saved visualization to " + os.path.join(base_dir, 'results', 'ppg_visualization_report.png'))
    print("Pipeline Complete.")

if __name__ == '__main__':
    main()
