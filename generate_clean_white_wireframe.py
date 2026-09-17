"""
generate_clean_white_wireframe.py
=================================
Generates a crisp, publication-grade facial mesh wireframe on a clean white
background with highlighted forehead and bilateral cheek (malar) microvascular ROIs.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon, FancyBboxPatch

def create_publication_wireframe(output_path="results/figures/fig1_roi_wireframe.png"):
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300, facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.set_xlim(-5, 15)
    ax.set_ylim(-1, 12)
    ax.axis('off')

    # Title & Subtitle in clean academic font
    ax.text(5.0, 11.4, "MediaPipe 468-Point Facial Mesh & Microvascular ROI Extraction", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1A365D', fontfamily='serif')
    ax.text(5.0, 10.8, "Anatomical mapping of dermal capillary beds optimized for Remote Photoplethysmography (rPPG)", 
            ha='center', va='center', fontsize=10, fontstyle='italic', color='#4A5568', fontfamily='serif')

    # Draw Stylized Facial Contour & Mesh on Left / Center
    # Face boundary
    theta = np.linspace(0, 2*np.pi, 200)
    # Parametric face shape
    x_face = 5.0 + 3.4 * np.cos(theta) * (1 - 0.15 * np.sin(theta))
    y_face = 5.2 + 4.6 * np.sin(theta) * (1 + 0.1 * np.cos(theta)**2)
    ax.plot(x_face, y_face, color='#CBD5E0', lw=1.8, zorder=2)
    ax.fill(x_face, y_face, color='#F8FAFC', zorder=1)

    # Eyes
    # Left eye
    x_eye_l = np.linspace(3.1, 4.3, 30)
    y_eye_l_top = 6.2 + 0.25 * np.sin(np.pi * (x_eye_l - 3.1) / 1.2)
    y_eye_l_bot = 6.2 - 0.25 * np.sin(np.pi * (x_eye_l - 3.1) / 1.2)
    ax.plot(x_eye_l, y_eye_l_top, color='#A0AEC0', lw=1.2, zorder=3)
    ax.plot(x_eye_l, y_eye_l_bot, color='#A0AEC0', lw=1.2, zorder=3)
    ax.scatter([3.7], [6.2], s=25, color='#4A5568', zorder=4)

    # Right eye
    x_eye_r = np.linspace(5.7, 6.9, 30)
    y_eye_r_top = 6.2 + 0.25 * np.sin(np.pi * (x_eye_r - 5.7) / 1.2)
    y_eye_r_bot = 6.2 - 0.25 * np.sin(np.pi * (x_eye_r - 5.7) / 1.2)
    ax.plot(x_eye_r, y_eye_r_top, color='#A0AEC0', lw=1.2, zorder=3)
    ax.plot(x_eye_r, y_eye_r_bot, color='#A0AEC0', lw=1.2, zorder=3)
    ax.scatter([6.3], [6.2], s=25, color='#4A5568', zorder=4)

    # Nose ridge & tip
    ax.plot([5.0, 5.0], [6.4, 4.4], color='#CBD5E0', lw=1.2, ls='--', zorder=3)
    ax.plot([4.6, 5.0, 5.4], [4.3, 4.1, 4.3], color='#A0AEC0', lw=1.4, zorder=3)

    # Lips
    x_lip = np.linspace(4.2, 5.8, 30)
    y_lip_top = 2.8 + 0.25 * np.sin(np.pi * (x_lip - 4.2) / 1.6)
    y_lip_mid = 2.8 * np.ones_like(x_lip)
    y_lip_bot = 2.8 - 0.3 * np.sin(np.pi * (x_lip - 4.2) / 1.6)
    ax.plot(x_lip, y_lip_top, color='#A0AEC0', lw=1.2, zorder=3)
    ax.plot(x_lip, y_lip_mid, color='#CBD5E0', lw=1.0, zorder=3)
    ax.plot(x_lip, y_lip_bot, color='#A0AEC0', lw=1.2, zorder=3)

    # Background Mesh Triangulation (Subtle gray lines & landmark points)
    np.random.seed(42)
    # Generate structured landmark grid inside the face
    grid_x = []
    grid_y = []
    for r in np.linspace(0.2, 0.85, 9):
        for a in np.linspace(0, 2*np.pi, 24, endpoint=False):
            gx = 5.0 + r * 3.1 * np.cos(a) * (1 - 0.15 * np.sin(a))
            gy = 5.2 + r * 4.2 * np.sin(a) * (1 + 0.1 * np.cos(a)**2)
            grid_x.append(gx)
            grid_y.append(gy)
            
    grid_x = np.array(grid_x)
    grid_y = np.array(grid_y)
    
    # Scatter subtle mesh points
    ax.scatter(grid_x, grid_y, s=4, color='#94A3B8', alpha=0.6, zorder=2)
    
    # Connect nearby mesh points to look like 3D facial topology
    from scipy.spatial import Delaunay
    points = np.column_stack([grid_x, grid_y])
    tri = Delaunay(points)
    for simplex in tri.simplices:
        # Check if triangle is inside face bounds
        pts = points[simplex]
        if np.max(np.linalg.norm(pts - np.array([5.0, 5.2]), axis=1)) < 4.2:
            ax.plot([pts[0,0], pts[1,0], pts[2,0], pts[0,0]], 
                    [pts[0,1], pts[1,1], pts[2,1], pts[0,1]], 
                    color='#E2E8F0', lw=0.6, alpha=0.7, zorder=2)

    # -------------------------------------------------------------
    # HIGHLIGHTED REGIONS OF INTEREST (ROIs)
    # -------------------------------------------------------------
    # 1. Upper Forehead ROI
    forehead_pts = np.array([
        [3.6, 7.8],
        [4.3, 8.4],
        [5.7, 8.4],
        [6.4, 7.8],
        [6.0, 7.2],
        [4.0, 7.2]
    ])
    poly_forehead = Polygon(forehead_pts, closed=True, 
                            facecolor='#38A169', edgecolor='#22543D', alpha=0.35, lw=2.0, zorder=5)
    ax.add_patch(poly_forehead)
    ax.scatter(forehead_pts[:,0], forehead_pts[:,1], s=20, color='#22543D', zorder=6)

    # 2. Left Malar / Cheek ROI
    l_cheek_pts = np.array([
        [2.6, 5.4],
        [3.8, 5.5],
        [3.9, 4.1],
        [2.8, 3.9]
    ])
    poly_l_cheek = Polygon(l_cheek_pts, closed=True, 
                           facecolor='#3182CE', edgecolor='#1A365D', alpha=0.35, lw=2.0, zorder=5)
    ax.add_patch(poly_l_cheek)
    ax.scatter(l_cheek_pts[:,0], l_cheek_pts[:,1], s=20, color='#1A365D', zorder=6)

    # 3. Right Malar / Cheek ROI
    r_cheek_pts = np.array([
        [6.2, 5.5],
        [7.4, 5.4],
        [7.2, 3.9],
        [6.1, 4.1]
    ])
    poly_r_cheek = Polygon(r_cheek_pts, closed=True, 
                           facecolor='#3182CE', edgecolor='#1A365D', alpha=0.35, lw=2.0, zorder=5)
    ax.add_patch(poly_r_cheek)
    ax.scatter(r_cheek_pts[:,0], r_cheek_pts[:,1], s=20, color='#1A365D', zorder=6)

    # -------------------------------------------------------------
    # CALLOUT BOXES & DESCRIPTIVE LEGENDS (RIGHT SIDE)
    # -------------------------------------------------------------
    # Forehead Callout
    ax.annotate("ROI 1: Upper Forehead Zone\n• Landmarks: 10, 338, 297, 332, 284, 251\n• High dermal capillary density\n• Minimal non-rigid facial expression distortion",
                xy=(5.0, 7.8), xytext=(9.2, 8.2),
                arrowprops=dict(arrowstyle="->", color="#22543D", lw=1.5, connectionstyle="arc3,rad=-0.1"),
                fontsize=9.5, fontfamily='serif', color='#1A202C',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#F0FFF4", edgecolor="#38A169", lw=1.2))

    # Bilateral Cheek Callout
    ax.annotate("ROI 2 & 3: Bilateral Malar Zones\n• Left: 116, 123, 147, 187, 205\n• Right: 345, 352, 376, 411, 425\n• Prominent transverse facial artery perfusion\n• Robust SNR under variable head yaw",
                xy=(3.4, 4.7), xytext=(9.2, 4.7),
                arrowprops=dict(arrowstyle="->", color="#1A365D", lw=1.5, connectionstyle="arc3,rad=0.15"),
                fontsize=9.5, fontfamily='serif', color='#1A202C',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#EBF8FF", edgecolor="#3182CE", lw=1.2))

    # Feature Averaging Note
    ax.annotate("Spatial Noise Reduction:\n• Pixel averaging: SNR gain ~ √N (≥ +18 dB)\n• Excludes ocular/oral non-vascular regions\n• Real-time tracking at 30 FPS via MediaPipe",
                xy=(5.0, 2.8), xytext=(9.2, 1.4),
                arrowprops=dict(arrowstyle="->", color="#4A5568", lw=1.2, ls="--"),
                fontsize=9.0, fontfamily='serif', color='#2D3748',
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#EDF2F7", edgecolor="#A0AEC0", lw=1.0))

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, facecolor='#ffffff', bbox_inches='tight')
    plt.close()
    print(f"Publication wireframe successfully saved to {output_path}")

if __name__ == "__main__":
    create_publication_wireframe()
