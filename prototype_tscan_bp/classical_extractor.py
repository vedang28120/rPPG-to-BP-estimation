"""
Classical rPPG Video Extractor Module (Synchronized with Smartphone Application)
Implements:
  1. MediaPipe Face Mesh anatomical polygon ROI masks (Forehead, Left Cheek, Right Cheek)
     matching FaceLandmarkTracker.kt in the Android application.
  2. Cubic Spline Resampling to 125 Hz uniform grid (pos_engine.py).
  3. Plane-Orthogonal-to-Skin (POS), CHROM, and GREEN projections.
  4. Dual-Stream Filter Architecture:
     - Path A: Fundamental Heart Rate (4th order Butterworth + High-res Welch PSD + Pan-Tompkins MWI)
     - Path B: Morphology Preservation (DWT BayesShrink Wavelet + Smoothness Priors SPA + Savitzky-Golay + [PPG, vPPG, aPPG] derivatives)
"""

import os
import sys
import cv2
import numpy as np
from scipy import signal, sparse
import scipy.sparse.linalg
from scipy.interpolate import CubicSpline
import pywt

# Protobuf compatibility layer for MediaPipe
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
try:
    import google.protobuf.message_factory
    import google.protobuf.descriptor
    import google.protobuf.symbol_database

    if not hasattr(google.protobuf.message_factory.MessageFactory, 'GetPrototype'):
        google.protobuf.message_factory.MessageFactory.GetPrototype = lambda self, descriptor: google.protobuf.message_factory.GetMessageClass(descriptor)
    if not hasattr(google.protobuf.symbol_database.SymbolDatabase, 'GetPrototype'):
        google.protobuf.symbol_database.SymbolDatabase.GetPrototype = lambda self, descriptor: google.protobuf.message_factory.GetMessageClass(descriptor)
    if not hasattr(google.protobuf.descriptor.FieldDescriptor, 'label'):
        google.protobuf.descriptor.FieldDescriptor.label = property(lambda self: getattr(self, '_label', 1))
except Exception:
    pass

import mediapipe as mp

# Anatomical landmark indices matching Android app FaceLandmarkTracker.kt
FOREHEAD_INDICES = [54, 103, 67, 109, 10, 338, 297, 332, 284, 298, 333, 299, 337, 151, 108, 69, 104, 68]
LEFT_CHEEK_INDICES = [116, 117, 118, 119, 100, 126, 209, 49, 129, 203, 205]
RIGHT_CHEEK_INDICES = [345, 346, 347, 348, 329, 355, 429, 279, 358, 423, 425]


def detrend_spa(z, lambda_=100):
    """Smoothness Priors Approach for detrending a signal at 125 Hz."""
    T = len(z)
    if T < 10:
        return z - np.mean(z)
    I = sparse.eye(T, format='csr')
    D2 = sparse.diags([1, -2, 1], [0, 1, 2], shape=(T-2, T), format='csr')
    trend = scipy.sparse.linalg.spsolve(I + (lambda_**2) * D2.T.dot(D2), z)
    return z - trend


def bayes_shrink_denoise(signal_data, wavelet='sym8'):
    """BayesShrink adaptive soft thresholding wavelet denoising."""
    if len(signal_data) < 32:
        return signal_data
    coeffs = pywt.wavedec(signal_data, wavelet)
    cD1 = coeffs[-1]
    noise_sigma = np.median(np.abs(cD1 - np.median(cD1))) / 0.6745
    noise_var = noise_sigma ** 2
    denoised_coeffs = [coeffs[0]]

    for cD in coeffs[1:]:
        if len(cD) == 0:
            denoised_coeffs.append(cD)
            continue
        subband_var = np.var(cD)
        sig_var = max(subband_var - noise_var, 0)
        if sig_var == 0:
            threshold = np.max(np.abs(cD))
        else:
            sig_std = np.sqrt(sig_var)
            threshold = noise_var / sig_std
        denoised = pywt.threshold(cD, value=threshold, mode='soft')
        denoised_coeffs.append(denoised)

    reconstructed = pywt.waverec(denoised_coeffs, wavelet)
    if len(reconstructed) > len(signal_data):
        reconstructed = reconstructed[:len(signal_data)]
    elif len(reconstructed) < len(signal_data):
        reconstructed = np.pad(reconstructed, (0, len(signal_data) - len(reconstructed)), 'edge')
    return reconstructed


class ClassicalRPPGExtractor:
    """
    Classical Facial rPPG Extractor strictly matching the Android mobile application pipeline:
      - MediaPipe Face Mesh anatomical polygon tracking (Forehead, Cheeks)
      - Cubic Spline Resampling to 125 Hz uniform grid
      - True POS, CHROM, and GREEN projections
      - Dual-Stream filtering (Path A for HR/HRV, Path B for morphology & BP)
    """

    def __init__(self, method="pos", min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.method = method.lower()
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def extract_rgb_traces(self, video_path, max_duration_sec=None):
        """
        Extracts spatial average RGB traces across polygon-masked anatomical ROIs
        matching FaceLandmarkTracker.kt.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video at: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps):
            fps = 30.0

        max_frames = int(max_duration_sec * fps) if max_duration_sec else None
        rgb_traces = []
        timestamps = []
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or (max_frames and frame_idx >= max_frames):
                break

            h, w = frame.shape[:2]
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                
                # Build polygon mask for Forehead, Left Cheek, Right Cheek
                mask = np.zeros((h, w), dtype=np.uint8)
                
                # Helper to convert normalized landmark list to integer points
                def get_pts(indices):
                    pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in indices], dtype=np.int32)
                    return np.clip(pts, [0, 0], [w - 1, h - 1])

                cv2.fillPoly(mask, [get_pts(FOREHEAD_INDICES)], 255)
                cv2.fillPoly(mask, [get_pts(LEFT_CHEEK_INDICES)], 255)
                cv2.fillPoly(mask, [get_pts(RIGHT_CHEEK_INDICES)], 255)

                # Compute masked mean RGB
                mask_bool = mask > 0
                if np.count_nonzero(mask_bool) > 50:
                    mean_r = float(np.mean(frame_rgb[:, :, 0][mask_bool]))
                    mean_g = float(np.mean(frame_rgb[:, :, 1][mask_bool]))
                    mean_b = float(np.mean(frame_rgb[:, :, 2][mask_bool]))
                    rgb_traces.append([mean_r, mean_g, mean_b])
                elif len(rgb_traces) > 0:
                    rgb_traces.append(rgb_traces[-1])
                else:
                    rgb_traces.append([float(np.mean(frame_rgb[:, :, 0])), float(np.mean(frame_rgb[:, :, 1])), float(np.mean(frame_rgb[:, :, 2]))])
            elif len(rgb_traces) > 0:
                rgb_traces.append(rgb_traces[-1])
            else:
                rgb_traces.append([float(np.mean(frame_rgb[:, :, 0])), float(np.mean(frame_rgb[:, :, 1])), float(np.mean(frame_rgb[:, :, 2]))])

            # Store timestamp in seconds
            timestamps.append(frame_idx / fps)
            frame_idx += 1

        cap.release()

        if len(rgb_traces) < 15:
            raise ValueError(f"Too few valid frames ({len(rgb_traces)}) extracted from video {video_path}")

        return np.array(rgb_traces, dtype=np.float32), np.array(timestamps, dtype=np.float32), fps

    def process_video(self, video_path, method=None, max_duration_sec=None):
        """
        Executes the full mobile app pos_engine.py pipeline on video frames:
          1. Extraction of polygon-masked RGB traces
          2. Cubic Spline Resampling to 125 Hz
          3. POS/CHROM/GREEN projection
          4. Dual-Stream Filtering (Path A: HR, Path B: Morphology)
        """
        chosen_method = (method or self.method).upper()
        rgb_traces, timestamps, raw_fps = self.extract_rgb_traces(video_path, max_duration_sec=max_duration_sec)

        # 1. Cubic Spline Resampling to strict 125 Hz uniform grid
        t_raw = timestamps
        t_norm = t_raw - t_raw[0]
        total_duration = t_norm[-1]
        target_fps = 125.0
        num_target_samples = int(total_duration * target_fps)
        if num_target_samples < int(target_fps * 1.6):
            num_target_samples = int(target_fps * 1.6)

        time_axis_125 = np.linspace(0, total_duration, num_target_samples)
        cs = CubicSpline(t_norm, rgb_traces, axis=0)
        rgb_signal_125 = cs(time_axis_125)
        new_fps = target_fps

        # 2. Classical Projections on 125 Hz uniform grid
        n_125 = len(rgb_signal_125)
        l = int(new_fps * 1.6)
        h = np.zeros(n_125)
        count = np.zeros(n_125)

        for i in range(n_125 - l + 1):
            window = rgb_signal_125[i:i+l]
            mean_c = np.mean(window, axis=0)
            mean_c[mean_c == 0] = 1e-5
            c_norm = window / mean_c
            R, G, B = c_norm[:, 0], c_norm[:, 1], c_norm[:, 2]

            if chosen_method == "POS":
                # True POS projection (Wang et al. 2016)
                X = G - B
                Y = G + B - 2 * R
                std_X, std_Y = np.std(X), np.std(Y)
                alpha = std_X / std_Y if std_Y != 0 else 0
                S = X + alpha * Y
            elif chosen_method == "CHROM":
                # Chrominance-based method (de Haan & Jeanne 2013)
                X = 3 * R - 2 * G
                Y = 1.5 * R + G - 1.5 * B
                std_X, std_Y = np.std(X), np.std(Y)
                alpha = std_X / std_Y if std_Y != 0 else 0
                S = X - alpha * Y
            elif chosen_method == "GREEN":
                # Green channel absorption
                S = -G
            else:
                raise ValueError(f"Unsupported extraction method: {chosen_method}")

            h[i:i+l] += S - np.mean(S)
            count[i:i+l] += 1

        count[count == 0] = 1
        raw_pos_125 = h / count

        # 3. Dual-Stream Filter Architecture (as implemented in Android pos_engine.py)
        nyq = 0.5 * new_fps

        # Path A: Fundamental Heart Rate Filter (4th order Butterworth bandpass 0.75 - 3.0 Hz)
        low_hr = 0.75 / nyq
        high_hr = 3.0 / nyq
        b_hr, a_hr = signal.butter(4, [low_hr, high_hr], btype='band')
        filtered_pos_hr = signal.filtfilt(b_hr, a_hr, raw_pos_125, padtype='odd', padlen=min(150, len(raw_pos_125)-1))

        # Path B: Morphology Preservation Filter for Neural BP Estimation
        raw_pos_125_denoised = bayes_shrink_denoise(raw_pos_125, wavelet='sym8')
        detrended_pos = detrend_spa(raw_pos_125_denoised, lambda_=100)
        filtered_pos_morph = signal.savgol_filter(detrended_pos, window_length=min(21, len(detrended_pos) if len(detrended_pos) % 2 != 0 else len(detrended_pos) - 1), polyorder=3)

        # 4. Extract Heart Rate via High-Resolution Welch PSD & Pan-Tompkins MWI
        hr = self.extract_hr(filtered_pos_hr, new_fps)

        # Return morphology-preserved signal at 125 Hz for BP engine, sampling rate, BPM, and RGB
        return filtered_pos_morph, new_fps, hr, rgb_traces

    def extract_hr(self, filtered_signal, fs):
        """
        Extracts heart rate using smartphone app's high-resolution Welch PSD (nfft=8192)
        and Pan-Tompkins peak refinement with 20% ectopic artifact rejection.
        """
        # Frequency-Domain HR Extraction (Welch's PSD with 8192-point FFT)
        f, pxx = signal.welch(filtered_signal, fs=fs, nperseg=min(len(filtered_signal), int(fs * 10)), nfft=8192)
        hr_band_idx = np.where((f >= 0.75) & (f <= 3.0))[0]

        if len(hr_band_idx) > 0:
            f_max = f[hr_band_idx[np.argmax(pxx[hr_band_idx])]]
            hr_fft = float(f_max * 60.0)
        else:
            hr_fft = 75.0

        # Time-Domain Pan-Tompkins Peak Refinement
        diff_signal = np.append(np.diff(filtered_signal), 0)
        squared_signal = diff_signal ** 2
        window_len = max(1, int(0.15 * fs))
        mwi = np.convolve(squared_signal, np.ones(window_len)/window_len, mode='same')
        threshold = np.mean(mwi) + 0.5 * np.std(mwi)
        mwi_peaks, _ = signal.find_peaks(mwi, height=threshold, distance=int(fs * 0.333))

        refined_peaks = []
        search_window = int(0.15 * fs)
        for p in mwi_peaks:
            start = max(0, p - search_window)
            end = min(len(filtered_signal), p + search_window)
            local_peak = start + np.argmax(filtered_signal[start:end])
            if len(refined_peaks) == 0 or local_peak != refined_peaks[-1]:
                refined_peaks.append(local_peak)

        peaks = np.array(refined_peaks)
        if len(peaks) > 2:
            ibis_ms = (np.diff(peaks) / fs) * 1000.0
            median_ibi = np.median(ibis_ms)
            valid_ibis = ibis_ms[(ibis_ms >= median_ibi * 0.8) & (ibis_ms <= median_ibi * 1.2)]
            if len(valid_ibis) > 1:
                hr_time = 60000.0 / np.mean(valid_ibis)
                # Combine FFT and time domain if both are physiologically consistent
                if abs(hr_time - hr_fft) < 15.0:
                    return float(round((hr_fft + hr_time) / 2.0, 1))

        return float(round(hr_fft, 1))

    def close(self):
        """Releases MediaPipe FaceMesh resources."""
        if hasattr(self, 'face_mesh') and self.face_mesh:
            self.face_mesh.close()
