"""
Optical Liveness & Anti-Spoofing Detector
Computes Eye-Aspect-Ratio (EAR) blink kinematics and 3D facial mesh depth variance to defeat 2D spoof attacks.
"""

import numpy as np

def calculate_ear(eye_landmarks_8):
    """
    Computes Eye Aspect Ratio (EAR) from 4 standard eye points [p33, p133, p159, p145].
    eye_landmarks_8: [x33, y33, x133, y133, x159, y159, x145, y145]
    """
    p33 = np.array([eye_landmarks_8[0], eye_landmarks_8[1]])
    p133 = np.array([eye_landmarks_8[2], eye_landmarks_8[3]])
    p159 = np.array([eye_landmarks_8[4], eye_landmarks_8[5]])
    p145 = np.array([eye_landmarks_8[6], eye_landmarks_8[7]])
    
    vertical = np.linalg.norm(p159 - p145)
    horizontal = np.linalg.norm(p33 - p133)
    if horizontal == 0:
        return 0.0
    return float(vertical / horizontal)

def verify_liveness(ear_sequence, nose_z_sequence, ear_std_threshold=0.001, depth_var_threshold=1e-5):
    """
    Evaluates dynamic motion criteria over a sliding sequence.
    
    Returns:
        is_live: Boolean flag indicating passing liveness test.
        diagnostics: Dictionary containing measured standard deviations.
    """
    if len(ear_sequence) == 0 or len(nose_z_sequence) == 0:
        return False, {"reason": "empty_sequence"}
        
    std_ear = float(np.std(ear_sequence))
    var_depth = float(np.var(nose_z_sequence))
    
    # 2D paper/screen spoofs are mathematically static (< ear_std_threshold) and planar (< depth_var_threshold)
    is_live = (std_ear >= ear_std_threshold) and (var_depth >= depth_var_threshold)
    
    return is_live, {
        "std_ear": std_ear,
        "var_depth": var_depth,
        "passed": is_live
    }
