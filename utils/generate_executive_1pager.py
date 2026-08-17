"""
Executive 1-Page Summary Flyer / Factsheet Generator
Compiles a publication-grade, single-page executive summary PDF:
'presentation/EXECUTIVE_SUMMARY_1PAGER.pdf'
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(ROOT_DIR, 'results', 'figures')
PRESENTATION_DIR = os.path.join(ROOT_DIR, 'presentation')
TARGET_PDF = os.path.join(PRESENTATION_DIR, 'EXECUTIVE_SUMMARY_1PAGER.pdf')


def build_executive_1pager(output_path=TARGET_PDF):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'ExecTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=1,
        textColor=colors.HexColor('#0F2942'),
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'ExecSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor('#2563EB'),
        spaceAfter=6
    )

    section_header = ParagraphStyle(
        'ExecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0F2942'),
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'ExecBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.2,
        alignment=4,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=3
    )

    bullet_text = ParagraphStyle(
        'ExecBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.8,
        textColor=colors.HexColor('#1F2937'),
        leftIndent=8,
        spaceAfter=1.5
    )

    callout_text = ParagraphStyle(
        'ExecCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.5,
        alignment=1,
        textColor=colors.HexColor('#1E3A8A')
    )

    story = []

    # Title Banner
    story.append(Paragraph("MOBILE rPPG TO CUFFLESS BLOOD PRESSURE ESTIMATION", title_style))
    story.append(Paragraph("Researchers: Vedang Bhatt (Student of CSE Dept.), Anubhav Shrivastav (Student of CSE Dept.) &bull; Project: vedang28120/rPPG-to-BP-estimation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F2942'), spaceAfter=5))

    # 2-Column Table for Overview & Problem
    col1_content = [
        Paragraph("1. THE CLINICAL CHALLENGE", section_header),
        Paragraph("Hypertension impacts <b>1.28 billion adults</b> globally and is the primary driver of strokes and heart failure. Traditional cuff sphygmomanometers cause sleep disruption and vascular occlusion. Camera-based remote photoplethysmography (rPPG) enables continuous, touchless monitoring from standard 30 FPS smartphone video.", body_text),
        Paragraph("2. SYSTEM ARCHITECTURE & INNOVATIONS", section_header),
        Paragraph("&bull; <b>Optical State Machine:</b> Camera2 AE/AWB Convergence-Hold-Lock eliminates ISP gain jitter.", bullet_text),
        Paragraph("&bull; <b>Facial Tracking:</b> 468-point MediaPipe mesh tracks forehead ROI to isolate microvascular perfusion.", bullet_text),
        Paragraph("&bull; <b>Chrominance Projection:</b> POS cancels specular reflections; TS-CAN attention handles motion.", bullet_text),
        Paragraph("&bull; <b>Physiological DSP:</b> 125 Hz PCHIP interpolation + BayesShrink DWT wavelet denoising.", bullet_text),
        Paragraph("&bull; <b>Deep Modeling:</b> MODEL-06 Dual-Branch 1D-ResNet + BiGRU + 4-Head MHSA with decoupled SBP/DBP heads.", bullet_text)
    ]

    col2_content = [
        Paragraph("3. VALIDATION BENCHMARKS (MCD-Iriun)", section_header),
        Paragraph("Subject-level validation with strict identity separation achieved:", body_text),
        Paragraph("&bull; <b>Systolic BP (SBP):</b> <b>10.12 mmHg MAE</b> | 14.58 mmHg RMSE (r = 0.388)", bullet_text),
        Paragraph("&bull; <b>Diastolic BP (DBP):</b> <b>5.91 mmHg MAE</b> | 8.54 mmHg RMSE (r = 0.355)", bullet_text),
        Paragraph("&bull; <b>Extractor SNR:</b> TS-CAN (10.4 dB) &gt; POS (8.9 dB) &gt; CHROM (5.8 dB)", bullet_text),
        Paragraph("4. EDGE DEPLOYMENT ARCHITECTURE", section_header),
        Paragraph("&bull; <b>Record-then-Process:</b> Decoupled 30 FPS buffering eliminates mobile JNI drops.", bullet_text),
        Paragraph("&bull; <b>On-Device Latency:</b> 120 ms single-shot TFLite inference on commodity hardware.", bullet_text),
        Paragraph("&bull; <b>Zero Extra Hardware:</b> Functions on standard front-facing RGB smartphone cameras.", bullet_text)
    ]

    # Two column overview table
    t_overview = Table([[col1_content, col2_content]], colWidths=[265, 265])
    t_overview.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 3))

    # Center Visual Overview
    fig_pipe = os.path.join(FIGURES_DIR, 'fig_pipeline_overview.png')
    if os.path.exists(fig_pipe):
        story.append(Image(fig_pipe, width=530, height=140))
        story.append(Spacer(1, 2))

    # Benchmark & Ablation Comparison Table
    bench_data = [
        ["Model Architecture", "Input Signal", "SBP MAE", "DBP MAE", "Subject SBP/DBP", "Clinical Status"],
        ["MODEL-01 (Demo MLP)", "Demographics Only", "16.82 mmHg", "9.41 mmHg", "15.90 / 8.85", "Population Mean Baseline"],
        ["MODEL-03 (1D-ResNet)", "1 x 1250 PPG", "14.20 mmHg", "8.12 mmHg", "13.10 / 7.40", "Convolutional Feature Extraction"],
        ["MODEL-05 (+BiGRU+MHSA)", "1 x 1250 PPG", "12.65 mmHg", "7.20 mmHg", "11.45 / 6.55", "Temporal Recurrence & Attention"],
        ["MODEL-06-SepHead (Ours)", "1 x 1250 PPG + Demo", "11.58 mmHg", "6.70 mmHg", "10.12 / 5.91", "Best Subject-Level Accuracy"]
    ]
    t_bench = Table(bench_data, colWidths=[120, 85, 65, 65, 85, 110])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 6.8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2.5),
        ('TOPPADDING', (0, 0), (-1, 0), 2.5),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EFF6FF')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('ALIGN', (2, 0), (4, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 6.5),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 3))

    # Bottom Callout Box: Template Collapse & Clinical Calibration
    callout_content = [
        [Paragraph("<b>CRITICAL SCIENTIFIC INSIGHT: TEMPLATE COLLAPSE & CLINICAL CALIBRATION</b>", callout_text)],
        [Paragraph(
            "<b>Root Cause of Template Collapse (Ben Ahmed et al.):</b> Facial microvasculature acts as a low-pass hydraulic reservoir (Windkessel damping), attenuating the dicrotic notch. Standard 8-bit RGB camera sensors impose an optical quantization floor (~0.39%) relative to 0.1–1.5% pulsatile AC variation. At 30 FPS (15 Hz Nyquist), the network collapses predictions toward population means without anchor points.<br/>"
            "<b>Clinical Solution:</b> Mandating a <b>Single-Point Personal Calibration</b> (one baseline cuff reading) anchors individual vascular compliance, unlocking continuous tracking compliant with <b>ISO 81060-2</b> (error &le; 5 mmHg).",
            body_text
        )]
    ]
    t_callout = Table(callout_content, colWidths=[530])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2563EB')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_callout)

    doc.build(story)
    print(f"[OK] Successfully built Executive 1-Pager PDF: {output_path}")


if __name__ == '__main__':
    build_executive_1pager()
