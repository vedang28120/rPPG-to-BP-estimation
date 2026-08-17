"""
TS-CAN Video rPPG Extractor Module
Handles facial video processing, frame difference computation, TS-CAN inference,
and signal post-processing (integration, bandpass filtering, HR estimation).
"""
import os
import cv2
import torch
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from scipy.sparse import spdiags
from prototype_tscan_bp.tscan_model import get_tscan_model

def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = max(1e-4, lowcut / nyq)
    high = min(0.999, highcut / nyq)
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(signal, lowcut=0.75, highcut=3.0, fs=30.0, order=3):
    if len(signal) < 15:
        return signal
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    padlen = min(len(signal) - 1, 3 * max(len(a), len(b)))
    return filtfilt(b, a, signal, padlen=padlen)

def detrend_signal(signal, Lambda=100):
    """Smoothness prior detrending algorithm."""
    T = len(signal)
    if T < 10:
        return signal - np.mean(signal)
    I = np.eye(T)
    D2 = spdiags(np.array([np.ones(T), -2*np.ones(T), np.ones(T)]), [0, 1, 2], T-2, T).toarray()
    detrended = (I - np.linalg.inv(I + (Lambda**2) * (D2.T @ D2))) @ signal
    return detrended

class TSCANExtractor:
    def __init__(self, checkpoint_path=None, device="cpu", frame_depth=10):
        self.device = device
        self.frame_depth = frame_depth
        if checkpoint_path is None:
            checkpoint_path = os.path.join(os.path.dirname(__file__), "checkpoints", "mtts_can.hdf5")
        
        self.model = get_tscan_model(checkpoint_path, device=device)
        self.face_cascade = None
        # Attempt to load Haar cascade if available
        cascade_path = getattr(cv2.data, 'haarcascades', '') + 'haarcascade_frontalface_default.xml'
        if os.path.exists(cascade_path):
            cc = cv2.CascadeClassifier(cascade_path)
            if not cc.empty():
                self.face_cascade = cc

    def extract_face_frames(self, video_path, target_dim=36, max_frames=None):
        """
        Reads video and crops face ROI to target_dim x target_dim.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError(f"Cannot open video file at: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps):
            fps = 30.0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if max_frames and total_frames > max_frames:
            total_frames = max_frames

        raw_frames = []
        face_box = None

        while True:
            ret, frame = cap.read()
            if not ret or (max_frames and len(raw_frames) >= max_frames):
                break

            h_orig, w_orig = frame.shape[:2]

            # Detect face with cascade if loaded
            if self.face_cascade is not None and face_box is None and len(raw_frames) % 30 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
                if len(faces) > 0:
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    x, y, w, h = faces[0]
                    pad_w = int(w * 0.1)
                    pad_h = int(h * 0.1)
                    face_box = (max(0, x + pad_w), max(0, y + pad_h), w - 2*pad_w, h - 2*pad_h)

            if face_box is not None:
                fx, fy, fw, fh = face_box
                cropped = frame[fy:fy+fh, fx:fx+fw]
            else:
                # Standard facial central ROI (top 15% to 85% height, 20% to 80% width)
                # This isolates the forehead, nose, and cheeks for rPPG
                y_start = int(h_orig * 0.15)
                y_end = int(h_orig * 0.85)
                x_start = int(w_orig * 0.20)
                x_end = int(w_orig * 0.80)
                cropped = frame[y_start:y_end, x_start:x_end]

            # Resize to target dimension (36x36)
            resized = cv2.resize(cropped, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            raw_frames.append(rgb)

        cap.release()
        return np.array(raw_frames, dtype=np.float32), fps

    def process_video(self, video_path, max_duration_sec=None):
        """
        Runs complete TS-CAN rPPG extraction pipeline on a video file.
        Returns:
            rppg_signal (np.ndarray): Continuous reconstructed pulse waveform
            fps (float): Video frame rate
            bpm (float): Estimated heart rate in beats per minute
            respiration_signal (np.ndarray): Extracted respiration waveform
        """
        max_frames = int(max_duration_sec * 30.0) if max_duration_sec else None
        frames, fps = self.extract_face_frames(video_path, target_dim=36, max_frames=max_frames)
        
        num_frames = len(frames)
        if num_frames < self.frame_depth + 1:
            raise ValueError(f"Video too short: {num_frames} frames found, need at least {self.frame_depth+1}")

        # Compute normalized difference frames: ΔS(t) = (S(t+1) - S(t)) / (S(t+1) + S(t) + 1e-6)
        diff_frames = (frames[1:] - frames[:-1]) / (frames[1:] + frames[:-1] + 1e-6)
        raw_app_frames = frames[:-1] # Appearance frames S(t)

        # Standardize difference frames (Z-score normalization)
        std_diff = np.std(diff_frames)
        if std_diff > 1e-6:
            diff_frames = (diff_frames - np.mean(diff_frames)) / std_diff

        # Trim to multiple of frame_depth (10)
        usable_len = (len(diff_frames) // self.frame_depth) * self.frame_depth
        diff_frames = diff_frames[:usable_len]
        raw_app_frames = raw_app_frames[:usable_len]

        # Convert to PyTorch tensors (N*T, C, H, W)
        motion_tensor = torch.from_numpy(diff_frames).permute(0, 3, 1, 2).float().to(self.device)
        app_tensor = torch.from_numpy(raw_app_frames).permute(0, 3, 1, 2).float().to(self.device)

        pulse_preds = []
        resp_preds = []

        batch_size = self.frame_depth * 10 # 100 frames per batch
        with torch.no_grad():
            for i in range(0, usable_len, batch_size):
                end_i = min(usable_len, i + batch_size)
                # Ensure batch is exact multiple of frame_depth
                cur_len = ((end_i - i) // self.frame_depth) * self.frame_depth
                if cur_len == 0:
                    break
                m_b = motion_tensor[i : i + cur_len]
                a_b = app_tensor[i : i + cur_len]

                p_b, r_b = self.model(m_b, a_b)
                pulse_preds.append(p_b.cpu().numpy().flatten())
                resp_preds.append(r_b.cpu().numpy().flatten())

        raw_pulse_deriv = np.concatenate(pulse_preds)
        raw_resp_deriv = np.concatenate(resp_preds)

        # 1. Integrate derivative to obtain continuous BVP pulse waveform: s(t) = cumsum(ds/dt)
        pulse_integrated = np.cumsum(raw_pulse_deriv)
        resp_integrated = np.cumsum(raw_resp_deriv)

        # 2. Detrend & Bandpass Filter (0.75 - 3.0 Hz for pulse, 0.15 - 0.5 Hz for resp)
        detrended_pulse = detrend_signal(pulse_integrated, Lambda=100)
        filtered_pulse = bandpass_filter(detrended_pulse, lowcut=0.75, highcut=3.0, fs=fps, order=3)
        
        detrended_resp = detrend_signal(resp_integrated, Lambda=300)
        filtered_resp = bandpass_filter(detrended_resp, lowcut=0.15, highcut=0.5, fs=fps, order=2)

        # 3. Estimate Heart Rate (BPM) via FFT Power Spectrum
        bpm = self.calculate_bpm(filtered_pulse, fps)

        return filtered_pulse, fps, bpm, filtered_resp

    @staticmethod
    def calculate_bpm(pulse_signal, fps):
        """Calculates heart rate in BPM using FFT power spectral density."""
        if len(pulse_signal) < int(fps * 2):
            return 75.0 # default fallback
        
        N = len(pulse_signal)
        freqs = np.fft.rfftfreq(N, 1.0 / fps)
        fft_vals = np.abs(np.fft.rfft(pulse_signal))

        # Physiological HR range: 45 BPM (0.75 Hz) to 180 BPM (3.0 Hz)
        valid_idx = np.where((freqs >= 0.75) & (freqs <= 3.0))[0]
        if len(valid_idx) == 0:
            return 75.0

        peak_idx = valid_idx[np.argmax(fft_vals[valid_idx])]
        peak_freq = freqs[peak_idx]
        bpm = peak_freq * 60.0
        return float(np.clip(bpm, 45.0, 180.0))
