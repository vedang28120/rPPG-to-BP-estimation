"""
Generate High-Resolution Publication & Presentation Assets
Produces clean, publication-grade figures for the academic paper and slide deck.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results', 'figures')
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'presentation', 'assets')
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Set high-quality styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8


def generate_pipeline_flowchart():
    """Generates a clean, modular architectural pipeline flowchart."""
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor='#ffffff')
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.5)
    ax.axis('off')

    stages = [
        ("1. Optical Acquisition", "Camera2 API (30 FPS)\nAE/AWB Convergence & Lock\n468 MediaPipe FaceMesh", "#EBF5FB", "#2E86C1"),
        ("2. Chrominance Extraction", "Spatial Mean ROI (Forehead)\nPOS Projection (Null Space)\nCHROM / TS-CAN Attention", "#EAF2F8", "#1B4F72"),
        ("3. Physiological DSP", "PCHIP Resampling (125 Hz)\nButterworth BPF (0.75-3.0 Hz)\nBayesShrink Wavelet DWT", "#E8F8F5", "#117A65"),
        ("4. Deep Sequence Modeling", "Dual-Branch 1D-ResNet\nBiGRU + MHSA (4 Heads)\nDecoupled SBP/DBP Heads", "#FEF9E7", "#B7950B"),
        ("5. Clinical BP Output", "Continuous SBP/DBP (mmHg)\nSignal Quality Index Gate\nSingle-Point Calibration", "#FDEDEC", "#922B21")
    ]

    for i, (title, desc, bg_color, border_color) in enumerate(stages):
        x = 0.4 + i * 2.1
        y = 0.8
        w = 1.9
        h = 2.8

        # Card rectangle
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
                                     facecolor=bg_color, edgecolor=border_color, linewidth=1.5)
        ax.add_patch(box)

        # Title Header
        ax.text(x + w/2, y + h - 0.35, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=border_color)

        # Dividing line
        ax.plot([x + 0.15, x + w - 0.15], [y + h - 0.7, y + h - 0.7], color=border_color, lw=0.8, alpha=0.5)

        # Description
        ax.text(x + w/2, y + (h - 0.7)/2, desc, ha='center', va='center',
                fontsize=8, color='#2C3E50', multialignment='center', linespacing=1.3)

        # Arrow to next stage
        if i < len(stages) - 1:
            ax.annotate('', xy=(x + w + 0.18, y + h/2), xytext=(x + w + 0.02, y + h/2),
                        arrowprops=dict(facecolor='#566573', edgecolor='#566573', width=1.5, headwidth=6, headlength=5))

    # Overall Title
    ax.text(5.5, 4.15, "End-to-End Mobile Remote Photoplethysmography to Blood Pressure Pipeline",
            ha='center', va='center', fontsize=12, fontweight='bold', color='#1C2833')

    plt.tight_layout()
    out_path1 = os.path.join(FIGURES_DIR, 'fig_pipeline_overview.png')
    out_path2 = os.path.join(ASSETS_DIR, 'fig_pipeline_overview.png')
    plt.savefig(out_path1, dpi=300, bbox_inches='tight')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Pipeline overview figure saved to: {out_path1}")


def generate_windkessel_and_quantization_diagram():
    """Generates the physical explanation diagram of Template Collapse and Windkessel damping."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor='#ffffff')

    # Panel A: Pulse Wave Damping (Arterial Tree vs Facial Microvasculature)
    t = np.linspace(0, 1.0, 500)
    # Finger PPG / Central Arterial with prominent dicrotic notch
    central_ppg = (np.exp(-((t - 0.18)/0.08)**2) * 1.0 +
                   0.45 * np.exp(-((t - 0.42)/0.09)**2) +
                   0.15 * np.sin(2 * np.pi * t))
    central_ppg = (central_ppg - central_ppg.min()) / (central_ppg.max() - central_ppg.min())

    # Facial rPPG (Heavily damped by Windkessel compliance + 30 FPS sampling)
    facial_rppg = np.exp(-((t - 0.22)/0.18)**2) * 0.9 + 0.15 * np.exp(-((t - 0.50)/0.25)**2)
    facial_rppg = (facial_rppg - facial_rppg.min()) / (facial_rppg.max() - facial_rppg.min())

    ax1.plot(t, central_ppg, label='Contact PPG (Finger / Arterial)', color='#C0392B', lw=2.2)
    ax1.plot(t, facial_rppg, label='Remote rPPG (Facial Microvascular)', color='#2980B9', lw=2.2, linestyle='--')

    # Annotate dicrotic notch
    ax1.annotate('Dicrotic Notch\n(Aortic Valve Closure)', xy=(0.42, 0.45), xytext=(0.55, 0.75),
                 arrowprops=dict(facecolor='#C0392B', shrink=0.05, width=1, headwidth=5),
                 fontsize=8.5, fontweight='bold', color='#C0392B')
    ax1.annotate('Severe Damping\n(Windkessel Effect)', xy=(0.48, 0.25), xytext=(0.60, 0.15),
                 arrowprops=dict(facecolor='#2980B9', shrink=0.05, width=1, headwidth=5),
                 fontsize=8.5, fontweight='bold', color='#2980B9')

    ax1.set_title('A. Hemodynamic Waveform Morphological Damping', fontsize=10.5, fontweight='bold', pad=10)
    ax1.set_xlabel('Normalized Cardiac Cycle Time (t / T)', fontsize=9)
    ax1.set_ylabel('Normalized Amplitude', fontsize=9)
    ax1.legend(loc='upper right', fontsize=8.5, framealpha=0.9)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Panel B: Camera Quantization Noise Floor vs Pulsatile AC Signal
    x_bars = ['Total DC\nReflection', 'Pulsatile AC\n(Hemoglobin)', 'Dicrotic\nNotch Feature', '8-bit Quant.\nNoise Floor']
    y_vals = [100.0, 1.2, 0.15, 0.39]
    colors = ['#7F8C8D', '#27AE60', '#E67E22', '#E74C3C']

    bars = ax2.bar(x_bars, y_vals, color=colors, width=0.55, edgecolor='#2C3E50', lw=1.1)
    ax2.set_yscale('log')
    ax2.set_ylim(0.05, 200)
    ax2.set_ylabel('Dynamic Range Magnitude (%) [Log Scale]', fontsize=9)
    ax2.set_title('B. Optical Dynamic Range vs Sensor Quantization', fontsize=10.5, fontweight='bold', pad=10)
    ax2.grid(True, which='both', linestyle=':', alpha=0.5, axis='y')

    for bar, val in zip(bars, y_vals):
        y_pos = val * 1.25 if val < 50 else val * 0.4
        ax2.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val}%', ha='center', va='bottom',
                 fontsize=8.5, fontweight='bold', color='#2C3E50')

    # Threshold horizontal line
    ax2.axhline(0.39, color='#E74C3C', linestyle=':', lw=1.5, alpha=0.8)
    ax2.text(1.8, 0.43, '8-bit Limit (1/256 ≈ 0.39%)', color='#E74C3C', fontsize=8, fontweight='bold')

    plt.tight_layout()
    out_path1 = os.path.join(FIGURES_DIR, 'fig_windkessel_damping.png')
    out_path2 = os.path.join(ASSETS_DIR, 'fig_windkessel_damping.png')
    plt.savefig(out_path1, dpi=300, bbox_inches='tight')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Windkessel & Quantization diagram saved to: {out_path1}")


def generate_model06_architecture_diagram():
    """Generates the MODEL-06 Dual-Branch ResNet + BiGRU + MHSA network schematic."""
    fig, ax = plt.subplots(figsize=(10.5, 4.8), facecolor='#ffffff')
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.8)
    ax.axis('off')

    # Input node
    ax.add_patch(patches.FancyBboxPatch((0.4, 1.8), 1.5, 1.2, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#EAEDED", edgecolor="#5D6D7E", lw=1.4))
    ax.text(1.15, 2.4, "Input Waveform\n(1 × 1250, 10s @ 125Hz)\n+ Demographics (3D)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#2C3E50')

    # Dual Branches
    # Branch 1 (Local Morphological)
    ax.add_patch(patches.FancyBboxPatch((2.4, 2.7), 1.8, 1.4, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#E8F8F5", edgecolor="#16A085", lw=1.4))
    ax.text(3.3, 3.4, "Branch 1: Local Morphology\nKernel=5, Stride=2\n3× ResBlock1D (32→128)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0E6251')

    # Branch 2 (Global Context)
    ax.add_patch(patches.FancyBboxPatch((2.4, 0.7), 1.8, 1.4, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#FEF5E7", edgecolor="#D35400", lw=1.4))
    ax.text(3.3, 1.4, "Branch 2: Global Context\nKernel=11, Dilated (1,2,2)\n3× ResBlock1D (32→128)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#7E5109')

    # Concatenation
    ax.add_patch(patches.FancyBboxPatch((4.6, 1.8), 1.1, 1.2, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#EBF5FB", edgecolor="#2980B9", lw=1.4))
    ax.text(5.15, 2.4, "Concatenate\n(B, 256, L)\nFeature Fusion",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1B4F72')

    # BiGRU + MHSA
    ax.add_patch(patches.FancyBboxPatch((6.0, 1.8), 1.5, 1.2, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#F4ECF7", edgecolor="#8E44AD", lw=1.4))
    ax.text(6.75, 2.4, "Temporal Attention\n2-Layer BiGRU (h=64)\n+ 4-Head MHSA\n+ Global Avg Pooling",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#512E5F')

    # Decoupled Heads
    # SBP Head
    ax.add_patch(patches.FancyBboxPatch((8.0, 2.7), 1.9, 1.3, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#FDEDEC", edgecolor="#C0392B", lw=1.4))
    ax.text(8.95, 3.35, "Decoupled SBP Head\nLinear(160→64) → ReLU\nLinear(64→1)\n→ SBP (mmHg)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#78281F')

    # DBP Head
    ax.add_patch(patches.FancyBboxPatch((8.0, 0.8), 1.9, 1.3, boxstyle="round,pad=0.05,rounding_size=0.1",
                                         facecolor="#EAF2F8", edgecolor="#2E86C1", lw=1.4))
    ax.text(8.95, 1.45, "Decoupled DBP Head\nLinear(160→64) → ReLU\nLinear(64→1)\n→ DBP (mmHg)",
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1B4F72')

    # Connection Arrows
    arrows = [
        ((1.9, 2.4), (2.38, 3.3)),
        ((1.9, 2.4), (2.38, 1.5)),
        ((4.2, 3.3), (4.58, 2.6)),
        ((4.2, 1.5), (4.58, 2.2)),
        ((5.7, 2.4), (5.98, 2.4)),
        ((7.5, 2.4), (7.98, 3.3)),
        ((7.5, 2.4), (7.98, 1.5)),
    ]
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(facecolor='#566573', edgecolor='#566573', width=1.2, headwidth=5, headlength=4.5))

    ax.text(5.25, 4.45, "MODEL-06-SepHead: Dual-Branch 1D-ResNet + BiGRU + MHSA Architecture",
            ha='center', va='center', fontsize=11.5, fontweight='bold', color='#1C2833')

    plt.tight_layout()
    out_path1 = os.path.join(FIGURES_DIR, 'fig_model06_architecture.png')
    out_path2 = os.path.join(ASSETS_DIR, 'fig_model06_architecture.png')
    plt.savefig(out_path1, dpi=300, bbox_inches='tight')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] MODEL-06 Architecture diagram saved to: {out_path1}")


def generate_benchmark_comparison_bar():
    """Generates benchmark comparison bar chart between extractors and models."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor='#ffffff')

    # Subplot 1: Extractor SNR (dB) on synchronized video dataset
    extractors = ['Green Channel', 'CHROM', 'POS', 'TS-CAN (Deep)']
    snr_vals = [2.4, 5.8, 8.9, 10.4]
    snr_colors = ['#BDC3C7', '#5DADE2', '#2E86C1', '#1B4F72']

    bars1 = ax1.bar(extractors, snr_vals, color=snr_colors, width=0.55, edgecolor='#2C3E50')
    ax1.set_title('A. Optical rPPG Extractor Signal-to-Noise Ratio (SNR)', fontsize=9.5, fontweight='bold')
    ax1.set_ylabel('Mean SNR (dB)', fontsize=8.5)
    ax1.set_ylim(0, 13)
    ax1.grid(True, linestyle=':', alpha=0.6, axis='y')
    for bar, val in zip(bars1, snr_vals):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.3, f'{val} dB', ha='center', fontsize=8, fontweight='bold')

    # Subplot 2: SBP & DBP MAE across ML Model Generations
    models = ['MODEL-01\n(Demo MLP)', 'MODEL-03\n(1D-ResNet)', 'MODEL-05\n(+BiGRU+MHSA)', 'MODEL-06\n(SepHead Dual-Branch)']
    sbp_mae = [16.8, 14.2, 12.6, 10.12]
    dbp_mae = [9.4, 8.1, 7.2, 5.91]

    x = np.arange(len(models))
    w = 0.35

    rects1 = ax2.bar(x - w/2, sbp_mae, w, label='Systolic (SBP) MAE', color='#C0392B', edgecolor='#2C3E50')
    rects2 = ax2.bar(x + w/2, dbp_mae, w, label='Diastolic (DBP) MAE', color='#2980B9', edgecolor='#2C3E50')

    ax2.set_title('B. Subject-Level MAE Across Model Generations (MCD-Iriun)', fontsize=9.5, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, fontsize=8)
    ax2.set_ylabel('MAE (mmHg) [Lower is Better]', fontsize=8.5)
    ax2.set_ylim(0, 20)
    ax2.legend(fontsize=8, loc='upper right')
    ax2.grid(True, linestyle=':', alpha=0.6, axis='y')

    # Annotate AAMI Threshold (8.0 mmHg standard)
    ax2.axhline(8.0, color='#E67E22', linestyle='--', lw=1.2, label='AAMI SP10 Standard (≤8 mmHg)')
    ax2.text(2.6, 8.3, 'AAMI Threshold (8 mmHg)', color='#E67E22', fontsize=7.5, fontweight='bold')

    for r in rects1:
        ax2.text(r.get_x() + r.get_width()/2, r.get_height() + 0.3, f'{r.get_height():.1f}', ha='center', fontsize=7.5, fontweight='bold', color='#78281F')
    for r in rects2:
        ax2.text(r.get_x() + r.get_width()/2, r.get_height() + 0.3, f'{r.get_height():.1f}', ha='center', fontsize=7.5, fontweight='bold', color='#1B4F72')

    plt.tight_layout()
    out_path1 = os.path.join(FIGURES_DIR, 'fig_extractor_benchmark_chart.png')
    out_path2 = os.path.join(ASSETS_DIR, 'fig_extractor_benchmark_chart.png')
    plt.savefig(out_path1, dpi=300, bbox_inches='tight')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Extractor benchmark chart saved to: {out_path1}")


if __name__ == '__main__':
    generate_pipeline_flowchart()
    generate_windkessel_and_quantization_diagram()
    generate_model06_architecture_diagram()
    generate_benchmark_comparison_bar()
    print("[ALL ASSETS GENERATED SUCCESSFULLY]")
