"""
PDF Report Generator Module
Compiles executive summaries, figure artifacts, numerical sample tables, and vital sign dashboards into a formal clinical PDF report.
"""

import os
import sys

try:
    from fpdf import FPDF
except ImportError:
    raise ImportError("The 'fpdf2' package is required. Install via: pip install fpdf2")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(ROOT_DIR, 'results', 'figures')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs')

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Mobile rPPG to Blood Pressure Estimation Pipeline', border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', border=0, ln=0, align='C')

def generate_full_pdf_report(output_pdf_path=None):
    if output_pdf_path is None:
        output_pdf_path = os.path.join(DOCS_DIR, "Project_Documentation.pdf")
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    pdf = PDFReport()
    pdf.add_page()

    # Section 1: Executive Summary
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '1. Executive Summary', ln=1)
    pdf.set_font('Helvetica', '', 11)
    summary_text = (
        "This project implements a non-invasive computer vision pipeline to estimate continuous "
        "Blood Pressure (BP) from standard facial video. By utilizing remote photoplethysmography (rPPG), "
        "the pipeline tracks subtle micro-color changes in facial Regions of Interest (ROIs) caused by "
        "the cardiac cycle. These optical signals are processed to extract a robust Blood Volume Pulse (BVP) "
        "waveform, which is then fed into a deep learning sequence model to predict continuous SBP and DBP."
    )
    pdf.multi_cell(0, 7, summary_text)
    pdf.ln(5)

    # Section 2: ROI Ingestion
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Video Ingestion & ROI Tracking', ln=1)
    pdf.set_font('Helvetica', '', 11)
    roi_text = (
        "MediaPipe Face Mesh tracks 468 landmarks in real-time. Upper Forehead and bilateral Cheek ROIs "
        "are dynamically isolated to minimize motion artifacts prior to chrominance extraction."
    )
    pdf.multi_cell(0, 7, roi_text)
    pdf.ln(3)

    fig1 = os.path.join(FIGURES_DIR, 'fig1_roi_wireframe.png')
    if os.path.exists(fig1):
        pdf.image(fig1, x=30, w=150)
    pdf.ln(5)

    # Section 3: POS & Signal Processing
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '3. POS Projection & Dual-Stream Filtering', ln=1)
    pdf.set_font('Helvetica', '', 11)
    pos_text = (
        "Spatial mean RGB traces undergo Plane-Orthogonal-to-Skin (POS) transformation to cancel specular "
        "reflections. A dual-stream filter performs Butterworth bandpass (0.75-3.0 Hz) and DWT BayesShrink "
        "wavelet denoising to preserve morphological features (systolic slope and dicrotic notch)."
    )
    pdf.multi_cell(0, 7, pos_text)
    pdf.ln(3)

    fig2 = os.path.join(FIGURES_DIR, 'fig2_signal_processing.png')
    if os.path.exists(fig2):
        pdf.image(fig2, x=30, w=150)
    pdf.ln(5)

    # Section 4: Deep Learning & Agreement
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '4. Deep Learning Sequence Modeling', ln=1)
    pdf.set_font('Helvetica', '', 11)
    dl_text = (
        "Sequences of standardized 125 Hz PPG windows are mapped to continuous SBP/DBP targets using "
        "a Dual-Branch 1D-ResNet with BiGRU temporal recurrence and Multi-Head Self-Attention."
    )
    pdf.multi_cell(0, 7, dl_text)
    pdf.ln(3)

    fig3 = os.path.join(FIGURES_DIR, 'fig3_bland_altman.png')
    if os.path.exists(fig3):
        pdf.image(fig3, x=40, w=130)
    pdf.ln(5)

    pdf.output(output_pdf_path)
    print(f"[PDF GENERATOR] Compiled PDF report to: {output_pdf_path}")

if __name__ == '__main__':
    generate_full_pdf_report()
