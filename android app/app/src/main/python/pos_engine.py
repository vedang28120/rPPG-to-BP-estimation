import numpy as np
from scipy import signal
from scipy import sparse
import scipy.sparse.linalg
from scipy.interpolate import CubicSpline
import pywt
def detrend_spa(z, lambda_=100):
    """
    Smoothness Priors Approach for detrending a signal.
    lambda_ controls the cutoff frequency (higher = lower cutoff).
    For 125 Hz, lambda_=100 is typically good for removing baseline < 0.5 Hz.
    """
    T = len(z)
    I = sparse.eye(T, format='csr')
    D2 = sparse.diags([1, -2, 1], [0, 1, 2], shape=(T-2, T), format='csr')
    # Solve (I + lambda^2 * D2^T * D2) * z_trend = z
    trend = scipy.sparse.linalg.spsolve(I + (lambda_**2) * D2.T.dot(D2), z)
    return z - trend

def calculate_ear(eye_landmarks):
    """
    eye_landmarks: [x33, y33, x133, y133, x159, y159, x145, y145]
    """
    p33 = np.array([eye_landmarks[0], eye_landmarks[1]])
    p133 = np.array([eye_landmarks[2], eye_landmarks[3]])
    p159 = np.array([eye_landmarks[4], eye_landmarks[5]])
    p145 = np.array([eye_landmarks[6], eye_landmarks[7]])
    
    vertical = np.linalg.norm(p159 - p145)
    horizontal = np.linalg.norm(p33 - p133)
    if horizontal == 0:
        return 0
    return vertical / horizontal

def check_liveness_ear(ear_sequence):
    if len(ear_sequence) == 0:
        return False
    ear_arr = np.array(ear_sequence)
    mean_ear = np.mean(ear_arr)
    std_ear = np.std(ear_arr)
    
    # Very lenient blink check: only fail if it's perfectly mathematically static (a photo)
    if std_ear < 1e-5:
        return False
        
    return True

def check_liveness_depth(nose_z_sequence):
    if len(nose_z_sequence) == 0:
        return False
    var_z = np.var(nose_z_sequence)
    # Lenient depth check for micro-movements
    if var_z < 1e-8:
        return False
    return True

def bayes_shrink_denoise(signal_data, wavelet='sym8'):
    if len(signal_data) == 0:
        return signal_data
        
    # Multi-level decomposition
    coeffs = pywt.wavedec(signal_data, wavelet)
    
    # Estimate noise variance from the first detail level (highest frequency CD1)
    cD1 = coeffs[-1]
    noise_sigma = np.median(np.abs(cD1 - np.median(cD1))) / 0.6745
    noise_var = noise_sigma ** 2
    
    denoised_coeffs = [coeffs[0]] # Keep approximation coefficients unmodified
    
    for cD in coeffs[1:]:
        n = len(cD)
        if n == 0:
            denoised_coeffs.append(cD)
            continue
            
        subband_var = np.var(cD)
        sig_var = max(subband_var - noise_var, 0)
        
        if sig_var == 0:
            threshold = np.max(np.abs(cD))
        else:
            sig_std = np.sqrt(sig_var)
            threshold = noise_var / sig_std
            
        # Adaptive soft thresholding
        denoised = pywt.threshold(cD, value=threshold, mode='soft')
        denoised_coeffs.append(denoised)
        
    reconstructed = pywt.waverec(denoised_coeffs, wavelet)
    
    # Handle length mismatch from waverec
    if len(reconstructed) > len(signal_data):
        reconstructed = reconstructed[:len(signal_data)]
    elif len(reconstructed) < len(signal_data):
        # Edge padding if slightly shorter
        reconstructed = np.pad(reconstructed, (0, len(signal_data) - len(reconstructed)), 'edge')
        
    return reconstructed

def check_sqi(filtered_pos, new_fps):
    f, pxx = signal.welch(filtered_pos, fs=new_fps, nperseg=len(filtered_pos))
    # Heart rate band: 0.75 Hz to 4.0 Hz
    valid_idx = np.where((f >= 0.75) & (f <= 4.0))[0]
    if len(valid_idx) == 0:
        return False
    
    peak_power = np.max(pxx[valid_idx])
    
    # Noise power: average power in the rest of the spectrum up to 6 Hz
    noise_idx = np.where((f > 0) & (f <= 6.0) & ~((f >= 0.75) & (f <= 4.0)))[0]
    if len(noise_idx) == 0:
        noise_power = 1e-8
    else:
        noise_power = np.mean(pxx[noise_idx])
        if noise_power == 0:
            noise_power = 1e-8
            
    snr = 10 * np.log10(peak_power / noise_power)
    # Strict physiological threshold
    if snr < 3.0:
        return False
    return True

def process_window(rgb_flat, timestamps, security_flat=None, session_state="INITIAL_VERIFICATION"):
    """
    Outputs:
        status_code: String ('SUCCESS', 'SPOOF_DETECTED', 'LOW_SQI')
        bvp_resampled: List of floats
        hr: Float heart rate
        hrv: Float HRV (RMSSD)
        rr: Float respiration rate
    """
    
    rgb_signal = np.array(rgb_flat).reshape(-1, 3)
    n = len(rgb_signal)
    
    # 0. Security Checks
    if security_flat is not None and len(security_flat) > 0:
        security_signal = np.array(security_flat).reshape(-1, 9)
        # Extract features: ear_features (0-7), nose_z (8)
        ear_sequence = []
        for i in range(n):
            ear_sequence.append(calculate_ear(security_signal[i, :8]))
        nose_z_sequence = security_signal[:, 8]
        
        if session_state == "INITIAL_VERIFICATION":
            if not check_liveness_depth(nose_z_sequence):
                return "SPOOF_DETECTED", [], [], 0.0, 0.0, 0.0
                
            if not check_liveness_ear(ear_sequence):
                return "SPOOF_DETECTED", [], [], 0.0, 0.0, 0.0
    
    # 1. Resampling Raw RGB Data to strict 125 Hz grid
    # Normalize timestamps to seconds
    t_raw = np.array(timestamps)
    t = (t_raw - t_raw[0]) / 1000.0
    
    # Force strictly 875 points to match LSTM input shape (7 sec * 125 Hz)
    target_points = 875
    if t[-1] <= 0:
        return "LOW_SQI", [], [], 0.0, 0.0, 0.0
        
    time_axis_125 = np.linspace(0, t[-1], target_points)
    # Dynamically adjust the true sampling rate to prevent frequency shift
    new_fps = target_points / t[-1]
    
    # Use Cubic Spline Interpolation on the raw RGB traces
    # to guarantee mathematically continuous 2nd derivatives (aPPG) for the Neural Network.
    cs = CubicSpline(t, rgb_signal, axis=0)
    rgb_signal_125 = cs(time_axis_125)
    
    # 2. POS Algorithm (on the strict 125 Hz uniform grid)
    n_125 = len(rgb_signal_125)
    l = int(new_fps * 1.6)
    
    if n_125 < l:
        return "LOW_SQI", [], [], 0.0, 0.0, 0.0
        
    h = np.zeros(n_125)
    count = np.zeros(n_125)
    for i in range(n_125 - l + 1):
        C = rgb_signal_125[i:i+l]
        mean_C = np.mean(C, axis=0)
        mean_C[mean_C == 0] = 1e-5
        C_norm = C / mean_C
        
        R = C_norm[:, 0]
        G = C_norm[:, 1]
        B = C_norm[:, 2]
        
        X = 3 * G - 2 * B
        Y = 1.5 * R + G - 1.5 * B
        
        std_X = np.std(X)
        std_Y = np.std(Y)
        alpha = std_X / std_Y if std_Y != 0 else 0
        
        S = X + alpha * Y
        h[i:i+l] += S - np.mean(S)
        count[i:i+l] += 1
        
    raw_pos_125 = h / count
    
    # 3. Dual-Filter Pipeline
    nyq = 0.5 * new_fps
    
    # Path A: The Fundamental Heart Rate Filter (Tight Band)
    low_hr = 0.75 / nyq
    high_hr = 3.0 / nyq
    b_hr, a_hr = signal.butter(4, [low_hr, high_hr], btype='band')
    filtered_pos_hr = signal.filtfilt(b_hr, a_hr, raw_pos_125, padtype='odd', padlen=150)
    
    # Path B: The Morphology Filter (Wide Band)
    # Apply DWT BayesShrink Denoising to eliminate dynamic camera exposure noise
    raw_pos_125_denoised = bayes_shrink_denoise(raw_pos_125, wavelet='sym8')
    
    # Advanced Filtering for Morphology (Preserves Peaks for BP derivatives)
    # 1. Remove slow baseline wander using Smoothness Priors (lambda=100 for 125Hz)
    detrended_pos = detrend_spa(raw_pos_125_denoised, lambda_=100)
    
    # 2. Savitzky-Golay Filter for high-frequency noise smoothing without peak rounding
    # Window length 21 (approx 0.16s at 125Hz), poly order 3
    filtered_pos_morph = signal.savgol_filter(detrended_pos, window_length=21, polyorder=3)
    
    # SQI Check on Path A
    if not check_sqi(filtered_pos_hr, new_fps):
        return "LOW_SQI", [], [], 0.0, 0.0, 0.0
    
    # Z-score normalization for Path A (Heart Rate, HRV)
    std_pos_hr = np.std(filtered_pos_hr)
    if std_pos_hr == 0:
        std_pos_hr = 1e-8
    normalized_pos_hr = (filtered_pos_hr - np.mean(filtered_pos_hr)) / std_pos_hr
    
    # 1. Spatial Derivatives
    ppg = filtered_pos_morph
    vppg = np.gradient(ppg)
    appg = np.gradient(vppg)

    # 2. Independent Z-score Normalization
    def z_score(arr):
        std_arr = np.std(arr)
        if std_arr == 0:
            std_arr = 1e-8
        return (arr - np.mean(arr)) / std_arr

    norm_ppg = z_score(ppg)
    norm_vppg = z_score(vppg)
    norm_appg = z_score(appg)

    # 3. Tensor Stacking: [PPG, vPPG, aPPG]
    multi_channel_tensor = np.column_stack((norm_ppg, norm_vppg, norm_appg))
    
    # 4. Extract Secondary Vitals
    # Frequency-Domain HR Extraction (Welch's PSD)
    f, pxx = signal.welch(normalized_pos_hr, fs=new_fps, nperseg=len(normalized_pos_hr), nfft=8192)
    # Restrict search band strictly between 0.75 Hz (45 BPM) and 3.0 Hz (180 BPM)
    hr_band_idx = np.where((f >= 0.75) & (f <= 3.0))[0]
    
    if len(hr_band_idx) > 0:
        f_max = f[hr_band_idx[np.argmax(pxx[hr_band_idx])]]
        hr = float(f_max * 60.0)
    else:
        hr = 0.0

    # Clinical-Grade Pan-Tompkins Style Peak Detection for HRV
    # 1. Differentiation to emphasize slopes
    diff_signal = np.diff(normalized_pos_hr)
    diff_signal = np.append(diff_signal, 0)
    
    # 2. Squaring to enhance dominant peaks and suppress noise
    squared_signal = diff_signal ** 2
    
    # 3. Moving Window Integration (~150ms window)
    window_len = int(0.15 * new_fps)
    mwi = np.convolve(squared_signal, np.ones(window_len)/window_len, mode='same')
    
    # 4. Adaptive Thresholding on MWI
    threshold = np.mean(mwi) + 0.5 * np.std(mwi)
    mwi_peaks, _ = signal.find_peaks(mwi, height=threshold, distance=int(new_fps * 0.333))
    
    # 5. Refine peaks back to the original waveform's local maxima
    refined_peaks = []
    search_window = int(0.15 * new_fps)
    for p in mwi_peaks:
        start = max(0, p - search_window)
        end = min(len(normalized_pos_hr), p + search_window)
        local_peak = start + np.argmax(normalized_pos_hr[start:end])
        if len(refined_peaks) == 0 or local_peak != refined_peaks[-1]:
            refined_peaks.append(local_peak)
            
    peaks = np.array(refined_peaks)
    
    if len(peaks) > 1:
        # Calculate IBIs in milliseconds
        ibis_ms = (np.diff(peaks) / new_fps) * 1000.0
        
        # Artifact Rejection (Ectopic Filtering)
        median_ibi = np.median(ibis_ms)
        lower_bound = median_ibi * 0.8
        upper_bound = median_ibi * 1.2
        
        # Keep only IBIs within 20% of the median
        valid_ibis = ibis_ms[(ibis_ms >= lower_bound) & (ibis_ms <= upper_bound)]
            
        # RMSSD Calculation on cleaned IBIs
        if len(valid_ibis) > 1:
            hrv = np.sqrt(np.mean(np.square(np.diff(valid_ibis))))
        else:
            hrv = 0.0
    else:
        hrv = 0.0
        
    # Crest Time (CT) Calculation
    crest_times = []
    if len(peaks) > 1:
        for i in range(1, len(peaks)):
            prev_peak = peaks[i-1]
            curr_peak = peaks[i]
            # Find trough (minimum) between prev_peak and curr_peak
            trough_idx = prev_peak + np.argmin(normalized_pos_hr[prev_peak:curr_peak])
            # Time from trough to peak in ms
            ct_ms = ((curr_peak - trough_idx) / new_fps) * 1000.0
            if 50.0 < ct_ms < 400.0: # Basic physiological artifact rejection
                crest_times.append(ct_ms)
                
    crest_time = np.mean(crest_times) if len(crest_times) > 0 else 0.0
        
    return "SUCCESS", normalized_pos_hr.tolist(), multi_channel_tensor.tolist(), float(hr), float(hrv), float(crest_time)
