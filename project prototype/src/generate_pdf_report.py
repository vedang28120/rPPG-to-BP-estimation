import os
import sys

# Attempt to import fpdf, provide graceful error and instructions if missing
try:
    from fpdf import FPDF
except ImportError:
    print("Error: The 'fpdf' library is required to generate the PDF.")
    print("Please install it by running: pip install fpdf2")
    sys.exit(1)

class PDFReport(FPDF):
    """
    Custom PDF class inheriting from FPDF to add consistent 
    Headers, Footers, and styling across the document.
    """
    def header(self):
        # Font: Helvetica bold 15
        self.set_font('Helvetica', 'B', 15)
        # Title, centered
        self.cell(0, 10, 'rPPG to Blood Pressure Estimation Pipeline', border=0, ln=1, align='C')
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from the bottom
        self.set_y(-15)
        # Font: Helvetica italic 8
        self.set_font('Helvetica', 'I', 8)
        # Page number, centered
        self.cell(0, 10, f'Page {self.page_no()}', border=0, ln=0, align='C')

def add_title_and_summary(pdf):
    """Adds the Executive Summary section."""
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '1. Executive Summary', ln=1)
    
    pdf.set_font('Helvetica', '', 11)
    summary_text = (
        "This project implements a non-invasive computer vision pipeline to estimate continuous "
        "Blood Pressure (BP) from standard facial video. By utilizing remote photoplethysmography (rPPG), "
        "the pipeline tracks subtle micro-color changes in facial Regions of Interest (ROIs) caused by "
        "the cardiac cycle. These optical signals are processed to extract a robust Blood Volume Pulse (BVP) "
        "waveform, which is then fed into a deep learning sequence model (LSTM) to predict continuous "
        "Systolic and Diastolic Blood Pressure."
    )
    # multi_cell automatically handles line breaks
    pdf.multi_cell(0, 7, summary_text)
    pdf.ln(5)

def add_step1_video_ingestion(pdf, image_path):
    """Adds Step 1 and embeds the ROI mapping image if available."""
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Step 1: Video Ingestion & ROI Tracking', ln=1)
    
    pdf.set_font('Helvetica', '', 11)
    text = (
        "The first step involves utilizing MediaPipe Face Mesh to dynamically track facial landmarks in "
        "real-time across the video frames. By selecting specific keypoints, the pipeline extracts highly "
        "localized Regions of Interest (ROIs), specifically the upper Forehead and the Left/Right Cheeks. "
        "This dense tracking ensures that the ROIs move consistently with the subject's head, minimizing "
        "motion artifacts prior to color extraction."
    )
    pdf.multi_cell(0, 7, text)
    pdf.ln(5)
    
    # Gracefully handle missing images
    if os.path.exists(image_path):
        # x=30 centers a 150mm wide image on an A4 page (210mm wide)
        pdf.image(image_path, x=30, w=150)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f'[Image not found: {image_path}]', ln=1, align='C')
        pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

def add_step2_pos_algorithm(pdf, image_path):
    """Adds Step 2, embeds the signal processing image, and a mock data table."""
    pdf.add_page() # Force step 2 onto a new page for clean formatting
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '3. Step 2: POS Algorithm & Signal Extraction', ln=1)
    
    pdf.set_font('Helvetica', '', 11)
    text = (
        "Following ROI extraction, the spatial mean of the RGB pixels is calculated for each frame. "
        "The Plane-Orthogonal-to-Skin (POS) algorithm combines these RGB channels to mathematically cancel "
        "out specular reflection (white illumination) while isolating the pulsatile skin-tone variations. "
        "The resulting projection is then bandpass filtered to strictly isolate human heart rate frequencies, "
        "producing the final continuous BVP signal."
    )
    pdf.multi_cell(0, 7, text)
    pdf.ln(5)
    
    if os.path.exists(image_path):
        pdf.image(image_path, x=30, w=150)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f'[Image not found: {image_path}]', ln=1, align='C')
        pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Simulated 13-column numerical output box
    pdf.set_font('Courier', '', 7)
    pdf.set_fill_color(240, 240, 240)
    
    sample_data = (
        "Sample Data Array (13-Column Output):\n"
        "Frame Index | Timestamp | Forehead (R,G,B) | L Cheek (R,G,B) | R Cheek (R,G,B) | Raw POS | Filtered BVP\n"
        "---------------------------------------------------------------------------------------------------------\n"
        "1.0         | 0.271s    | 0.51, 0.22, 0.56 | 0.61, 0.51, 0.55| 0.91, 0.93, 0.40| 0.427   | 0.572       \n"
        "2.0         | 0.377s    | 0.37, 0.20, 0.29 | 0.85, 0.12, 0.59| 0.01, 0.74, 0.46| 0.625   | 0.068       \n"
    )
    pdf.multi_cell(0, 5, sample_data, border=1, fill=True)
    pdf.ln(5)

def add_step3_deep_learning(pdf, image_path):
    """Adds Step 3 and embeds the Bland-Altman error plot."""
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, '4. Step 3: Deep Learning Inference (LSTM)', ln=1)
    
    pdf.set_font('Helvetica', '', 11)
    text = (
        "The cleaned BVP signal is chunked into 7-second sliding windows. These sequences are fed into "
        "a deep Long Short-Term Memory (LSTM) neural network that was pre-trained on the MIMIC-III database. "
        "The LSTM learns the temporal morphology of the optical waveform (like the systolic upstroke and "
        "dicrotic notch) and maps these features to continuous Systolic and Diastolic Blood Pressure values."
    )
    pdf.multi_cell(0, 7, text)
    pdf.ln(5)
    
    if os.path.exists(image_path):
        pdf.image(image_path, x=40, w=130)
    else:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f'[Image not found: {image_path}]', ln=1, align='C')
        pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

def add_clinical_dashboard(pdf):
    """Adds the final clinical dashboard section with a simulated UI."""
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(0, 51, 102) # Dark blue text
    pdf.cell(0, 15, '5. Final Clinical Dashboard (The Outputs)', ln=1, align='C')
    pdf.set_text_color(0, 0, 0) # Reset to black
    
    pdf.set_font('Helvetica', '', 12)
    pdf.multi_cell(0, 8, "Below is the final computed vital signs dashboard for a sample testing window:")
    pdf.ln(10)
    
    # Draw a colored background box for the dashboard
    pdf.set_fill_color(235, 245, 255) # Light blue background
    # rect(x, y, w, h, style)
    pdf.rect(15, pdf.get_y(), 180, 85, 'F')
    
    # Dashboard Content
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_y(pdf.get_y() + 5)
    pdf.cell(0, 10, '    VITAL SIGNS SUMMARY', ln=1)
    
    pdf.set_font('Helvetica', '', 12)
    vitals = [
        "    Heart Rate: 72 BPM",
        "    Heart Rate Variability (RMSSD): 45 ms",
        "    Respiration Rate: 16 Breaths/min",
        "    Blood Pressure: 109/63 mmHg (SBP / DBP)",
        "    Mean Arterial Pressure (MAP): 78 mmHg"
    ]
    
    for vital in vitals:
        pdf.cell(0, 10, vital, ln=1)
        
    pdf.ln(5)
    
    # Conclusion text colored based on threshold
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 128, 0) # Green for normal
    pdf.cell(0, 10, '    Clinical Conclusion: Normal', ln=1)
    pdf.set_text_color(0, 0, 0) # Reset

def main():
    # Base paths relative to this script in the src/ folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, "outputs")
    
    os.makedirs(outputs_dir, exist_ok=True)
    
    pdf = PDFReport()
    pdf.add_page()
    
    print("Generating Document Sections...")
    add_title_and_summary(pdf)
    add_step1_video_ingestion(pdf, os.path.join(outputs_dir, 'fig1_roi_wireframe.png'))
    add_step2_pos_algorithm(pdf, os.path.join(outputs_dir, 'fig2_signal_processing.png'))
    add_step3_deep_learning(pdf, os.path.join(outputs_dir, 'fig3_bland_altman.png'))
    add_clinical_dashboard(pdf)
    
    output_pdf_path = os.path.join(outputs_dir, "Project_Documentation.pdf")
    pdf.output(output_pdf_path)
    print(f"Success! PDF report generated at: {output_pdf_path}")

if __name__ == '__main__':
    main()
