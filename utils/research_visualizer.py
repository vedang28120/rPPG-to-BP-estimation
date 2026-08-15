"""
Research Plot Visualizer
Generates IEEE/Nature-styled research figures for facial wireframes, signal processing stages,
Bland-Altman error plots, 3D Takens phase-space attractors, Bayesian uncertainty bounds, and LDS distributions.
"""

import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.signal import find_peaks
import cv2

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(ROOT_DIR, 'results', 'figures')

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

def generate_roi_wireframe(image_path=None, output_path=None):
    """
    Applies MediaPipe Face Mesh, draws wireframe, and highlights Forehead and Cheek ROIs.
    """
    if output_path is None:
        output_path = os.path.join(FIGURES_DIR, "fig1_roi_wireframe.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    import mediapipe as mp
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    image = None
    if image_path and os.path.exists(image_path):
        image = cv2.imread(image_path)
    if image is None:
        video_path = os.path.join(ROOT_DIR, "data", "raw", "WIN_20260731_09_47_27_Pro.mp4")
        if os.path.exists(video_path):
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if ret:
                image = frame
            cap.release()

    if image is None:
        image = np.zeros((500, 500, 3), dtype=np.uint8)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.1
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        annotated_image = image.copy()

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=annotated_image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )

                h, w, _ = annotated_image.shape
                def get_bbox(indices):
                    x_coords = [int(face_landmarks.landmark[idx].x * w) for idx in indices]
                    y_coords = [int(face_landmarks.landmark[idx].y * h) for idx in indices]
                    return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

                fx1, fy1, fx2, fy2 = get_bbox([10, 109, 151, 338])
                lx1, ly1, lx2, ly2 = get_bbox([116, 117, 118, 119])
                rx1, ry1, rx2, ry2 = get_bbox([345, 346, 347, 348])

                cv2.rectangle(annotated_image, (fx1, fy1), (fx2, fy2), (0, 255, 0), 2)
                cv2.rectangle(annotated_image, (lx1, ly1), (lx2, ly2), (255, 0, 0), 2)
                cv2.rectangle(annotated_image, (rx1, ry1), (rx2, ry2), (255, 0, 0), 2)

    cv2.imwrite(output_path, annotated_image)
    print(f"[VISUALIZER] Saved ROI wireframe: {output_path}")

def generate_bland_altman(true_bp=None, pred_bp=None, output_path=None):
    """
    Generates Bland-Altman statistical agreement plot comparing True vs Predicted BP.
    """
    if output_path is None:
        output_path = os.path.join(FIGURES_DIR, "fig3_bland_altman.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    set_publication_style()

    if true_bp is None or pred_bp is None:
        np.random.seed(42)
        true_sbp = np.random.normal(120, 15, 200)
        pred_sbp = true_sbp + np.random.normal(0, 8, 200)
    else:
        true_sbp, pred_sbp = np.array(true_bp), np.array(pred_bp)

    mean_vals = (true_sbp + pred_sbp) / 2.0
    diff_vals = pred_sbp - true_sbp
    md = np.mean(diff_vals)
    sd = np.std(diff_vals)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(mean_vals, diff_vals, alpha=0.6, edgecolors='none', color='#1f77b4')
    ax.axhline(md, color='red', linestyle='--', label=f'Mean Bias: {md:.2f} mmHg')
    ax.axhline(md + 1.96 * sd, color='gray', linestyle=':', label=f'+1.96 SD: {md + 1.96 * sd:.2f}')
    ax.axhline(md - 1.96 * sd, color='gray', linestyle=':', label=f'-1.96 SD: {md - 1.96 * sd:.2f}')

    ax.set_title('Bland-Altman Agreement: Systolic BP')
    ax.set_xlabel('Mean of True and Predicted BP (mmHg)')
    ax.set_ylabel('Difference (Predicted - True) (mmHg)')
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[VISUALIZER] Saved Bland-Altman plot: {output_path}")

def generate_attractor_3d_plot(signal_1d=None, tau=2, output_path=None):
    """
    Renders a 3D phase-space attractor trajectory portrait [s(t), s(t-tau), s(t-2tau)].
    """
    if output_path is None:
        output_path = os.path.join(FIGURES_DIR, "fig5_topological_attractor.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    set_publication_style()

    if signal_1d is None:
        t = np.linspace(0, 6 * np.pi, 500)
        signal_1d = np.sin(t) + 0.3 * np.sin(2 * t) + 0.1 * np.random.randn(500)

    s = (signal_1d - np.mean(signal_1d)) / (np.std(signal_1d) + 1e-8)
    n = len(s)
    x = s[: n - 2 * tau]
    y = s[tau : n - tau]
    z = s[2 * tau :]

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z, color='#2ca02c', alpha=0.7, lw=1.2)
    ax.scatter(x[::10], y[::10], z[::10], c=np.arange(len(x[::10])), cmap='plasma', s=12)

    ax.set_title("Takens Delay Embedding: Cardiovascular Attractor", fontsize=14)
    ax.set_xlabel(r"$s(t)$")
    ax.set_ylabel(r"$s(t - \tau)$")
    ax.set_zlabel(r"$s(t - 2\tau)$")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[VISUALIZER] Saved 3D attractor portrait: {output_path}")

def generate_uncertainty_plot(true_bp=None, pred_mean=None, pred_std=None, output_path=None):
    """
    Generates a scatter plot with Bayesian predictive uncertainty error bars (±2 sigma).
    """
    if output_path is None:
        output_path = os.path.join(FIGURES_DIR, "fig6_bayesian_uncertainty.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    set_publication_style()

    if true_bp is None or pred_mean is None:
        np.random.seed(42)
        true_bp = np.linspace(90, 160, 40)
        pred_mean = true_bp + np.random.normal(0, 5, 40)
        pred_std = np.random.uniform(2.0, 7.0, 40)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(true_bp, pred_mean, yerr=2 * pred_std, fmt='o', color='#1f77b4',
                ecolor='#aec7e8', elinewidth=2, capsize=3, label=r'Prediction $\pm 2\sigma$ Uncertainty')
    ax.plot([80, 180], [80, 180], 'r--', label='Ideal 1:1 Identity')

    ax.set_title("Bayesian Heteroscedastic Predictions vs Ground Truth SBP", fontsize=14)
    ax.set_xlabel("Ground Truth SBP (mmHg)", fontsize=12)
    ax.set_ylabel("Predicted SBP (mmHg)", fontsize=12)
    ax.set_xlim(80, 180)
    ax.set_ylim(80, 180)
    ax.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[VISUALIZER] Saved Bayesian uncertainty plot: {output_path}")

def generate_lds_distribution_plot(raw_sbp=None, output_path=None):
    """
    Plots the empirical SBP label histogram alongside the Gaussian-smoothed LDS weight distribution.
    """
    if output_path is None:
        output_path = os.path.join(FIGURES_DIR, "fig7_lds_distribution.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    set_publication_style()

    if raw_sbp is None:
        np.random.seed(42)
        raw_sbp = np.random.normal(120, 12, 1000)

    from scipy.ndimage import gaussian_filter1d
    hist, bin_edges = np.histogram(raw_sbp, bins=40, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    smoothed = gaussian_filter1d(hist, sigma=2.0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(bin_centers, hist, width=(bin_edges[1] - bin_edges[0]), alpha=0.5, color='#3498db', label='Empirical Target Density')
    ax.plot(bin_centers, smoothed, color='#e74c3c', lw=2.5, label='LDS Smoothed Density ($p_{\mathrm{smooth}}$)')

    ax.set_title("Label Distribution Smoothing (LDS) for SBP Imbalance", fontsize=14)
    ax.set_xlabel("Systolic Blood Pressure (mmHg)", fontsize=12)
    ax.set_ylabel("Probability Density", fontsize=12)
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"[VISUALIZER] Saved LDS distribution plot: {output_path}")

if __name__ == '__main__':
    generate_roi_wireframe()
    generate_bland_altman()
    generate_attractor_3d_plot()
    generate_uncertainty_plot()
    generate_lds_distribution_plot()
