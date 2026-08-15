"""
Dynamic Face Mesh Tracker & Multi-ROI Sub-Patch Extractor
Utilizes MediaPipe Face Mesh to track 468 landmarks and extract 5 anatomical ROIs
with spatial sub-patching (10 distinct patches) for noise-robust rPPG tracking.
"""

import numpy as np
import cv2

# 5 Anatomical ROIs defined by MediaPipe landmark index groups
ROI_LANDMARKS = {
    'forehead': [10, 109, 151, 338],     # Upper Central Forehead
    'left_cheek': [116, 117, 118, 119],   # Left Zygomatic/Malar Region
    'right_cheek': [345, 346, 347, 348],  # Right Zygomatic/Malar Region
    'nose': [1, 2, 98, 327],              # Nasal Dorsum
    'chin': [152, 175, 200, 396]          # Mentalis/Chin Region
}

def get_roi_bounding_box(landmarks, indices, width, height):
    """
    Computes clamped integer pixel bounding box for a set of landmark indices.
    """
    xs = [int(landmarks.landmark[i].x * width) for i in indices]
    ys = [int(landmarks.landmark[i].y * height) for i in indices]
    x_min = max(0, min(xs))
    x_max = min(width, max(xs))
    y_min = max(0, min(ys))
    y_max = min(height, max(ys))
    return x_min, y_min, x_max, y_max

def extract_facial_rois(frame, landmarks, width, height, return_boxes=True, sub_patch=True):
    """
    Extracts spatial mean RGB values for 5 anatomical ROIs with optional sub-patching (10 patches).
    
    Args:
        frame: RGB image array (H, W, 3).
        landmarks: MediaPipe NormalizedLandmarkList.
        width: Frame width in pixels.
        height: Frame height in pixels.
        return_boxes: Whether to return bounding box coordinates.
        sub_patch: Whether to split each ROI into left and right sub-patches (10 patches total).
        
    Returns:
        mean_rgb: Average RGB vector [R, G, B] across all valid primary ROIs.
        roi_means_dict: Dictionary of per-ROI / per-sub-patch mean RGBs.
        roi_boxes: List of bounding box tuples (x_min, y_min, x_max, y_max).
    """
    roi_means_dict = {}
    roi_boxes = []
    all_means = []

    for name, indices in ROI_LANDMARKS.items():
        x_min, y_min, x_max, y_max = get_roi_bounding_box(landmarks, indices, width, height)
        if x_max > x_min and y_max > y_min:
            patch = frame[y_min:y_max, x_min:x_max]
            
            # Primary ROI spatial mean
            r = float(np.mean(patch[:, :, 0]))
            g = float(np.mean(patch[:, :, 1]))
            b = float(np.mean(patch[:, :, 2]))
            roi_means_dict[name] = [r, g, b]
            all_means.append([r, g, b])
            roi_boxes.append((x_min, y_min, x_max, y_max))
            
            # Sub-patching: Divide patch into Left and Right halves for spatial redundancy
            if sub_patch:
                w_mid = (x_max - x_min) // 2
                if w_mid > 0:
                    left_half = patch[:, :w_mid]
                    right_half = patch[:, w_mid:]
                    roi_means_dict[f"{name}_left"] = [
                        float(np.mean(left_half[:, :, 0])),
                        float(np.mean(left_half[:, :, 1])),
                        float(np.mean(left_half[:, :, 2]))
                    ]
                    roi_means_dict[f"{name}_right"] = [
                        float(np.mean(right_half[:, :, 0])),
                        float(np.mean(right_half[:, :, 1])),
                        float(np.mean(right_half[:, :, 2]))
                    ]
                else:
                    roi_means_dict[f"{name}_left"] = [r, g, b]
                    roi_means_dict[f"{name}_right"] = [r, g, b]
        else:
            roi_means_dict[name] = [0.0, 0.0, 0.0]
            if sub_patch:
                roi_means_dict[f"{name}_left"] = [0.0, 0.0, 0.0]
                roi_means_dict[f"{name}_right"] = [0.0, 0.0, 0.0]

    # Overall central robust mean across primary anatomical ROIs
    if len(all_means) > 0:
        mean_rgb = np.mean(all_means, axis=0)
    else:
        mean_rgb = np.array([0.0, 0.0, 0.0])

    if return_boxes:
        return mean_rgb, roi_means_dict, roi_boxes
    return mean_rgb, roi_means_dict
