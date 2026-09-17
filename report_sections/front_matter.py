"""
report_sections/front_matter.py
===============================
Generates Cover Page, Declaration, Certificate, Acknowledgments,
and Abstract with exact academic metadata and clean institutional text.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def build_cover_page(doc, logo_path):
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_top.paragraph_format.space_before = Pt(8)
    p_top.paragraph_format.space_after = Pt(2)
    r = p_top.add_run("A VOCATIONAL TRAINING REPORT\nON")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(14)
    r.font.bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(12)
    r_t = p_title.add_run('“LuminaBP: Non-Invasive Continuous Blood Pressure Estimation via Remote Photoplethysmography and Deep Learning”')
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(16)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(180, 0, 0)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(8)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run(
        "A Training Report Submitted to\n"
        "CHHATTISGARH SWAMI VIVEKANANDA TECHNICAL UNIVERSITY, BHILAI (C.G.), INDIA\n\n"
        "For the partial fulfillment of the award of degree\n"
        "BACHELOR OF TECHNOLOGY\n"
        "In\n"
        "COMPUTER SCIENCE & ENGINEERING"
    )
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True

    # Logo
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(6)
        p_logo.paragraph_format.space_after = Pt(6)
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Inches(1.25))

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_by.paragraph_format.space_before = Pt(4)
    p_by.paragraph_format.space_after = Pt(4)
    r_by = p_by.add_run("By\nVedang Bhatt\n(Roll No: 309302224050, Enrollment No: CE4669)\n\nUnder the Training of\nDr. Anurag Singh\nAssociate Professor, IIIT Naya Raipur\nTraining In-Charge")
    r_by.font.name = 'Times New Roman'
    r_by.font.size = Pt(12)
    r_by.font.bold = True

    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(12)
    p_dept.paragraph_format.space_after = Pt(0)
    r_dept = p_dept.add_run(
        "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING\n"
        "BHILAI INSTITUTE OF TECHNOLOGY, RAIPUR\n"
        "Village – Kendri, Near Abhanpur, Atal Nagar, Raipur – 493661 (C.G.) India\n\n"
        "BATCH 2024 - 2028"
    )
    r_dept.font.name = 'Times New Roman'
    r_dept.font.size = Pt(11)
    r_dept.font.bold = True

def build_declaration(doc, add_heading_chapter, add_body_p):
    add_heading_chapter(doc, "", "DECLARATION")
    
    add_body_p(doc, "I the undersigned solemnly declare that the Vocational Training report on “LuminaBP: Non-Invasive Continuous Blood Pressure Estimation via Remote Photoplethysmography and Deep Learning” is based on my training work carried out during my vocational duration under the supervision of Dr. Anurag Singh, Associate Professor from IIIT Naya Raipur.")
    add_body_p(doc, "I assert that the statements made and conclusions drawn are an outcome of the Vocational Training/Internship. I further declare that to the best of my knowledge and belief that this report does not contain any relevant work which has been submitted earlier.")
    
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(36)
    p_sp.paragraph_format.space_after = Pt(6)
    
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_sig.paragraph_format.line_spacing = 1.5
    r = p_sig.add_run("Signature              : _______________________\nStudent’s Name    : Mr. Vedang Bhatt\nRoll No.                 : 309302224050\nEnrollment No.      : CE4669")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

def build_certificate(doc, add_heading_chapter, add_body_p):
    add_heading_chapter(doc, "", "CERTIFICATE")
    
    add_body_p(doc, "This is to certify that the report of the vocational training on “LuminaBP: Non-Invasive Continuous Blood Pressure Estimation via Remote Photoplethysmography and Deep Learning” is the bonafide work carried out by Mr. Vedang Bhatt studying in 4th semester in Computer Science & Engineering branch at Bhilai Institute of Technology, Raipur, affiliated to Chhattisgarh Swami Vivekananda Technical University, Bhilai (C.G.), India under the guidance and supervision of Dr. Anurag Singh, Associate Professor at IIIT Naya Raipur.")
    
    add_body_p(doc, "To the best of my knowledge and belief the report:")
    p_b1 = doc.add_paragraph(style='List Bullet')
    p_b1.paragraph_format.line_spacing = 1.5
    r1 = p_b1.add_run("Embodies the original work of the candidate himself.")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    
    p_b2 = doc.add_paragraph(style='List Bullet')
    p_b2.paragraph_format.line_spacing = 1.5
    r2 = p_b2.add_run("Has duly been completed in full compliance with the training curriculum.")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(12)
    
    p_b3 = doc.add_paragraph(style='List Bullet')
    p_b3.paragraph_format.line_spacing = 1.5
    r3 = p_b3.add_run("Fulfills the requirements of the ordinance relating to vocational training/internship with respect to the university curriculum.")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(12)
    
    add_body_p(doc, "For being referred to the examiners.")

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(48)
    p_sp.paragraph_format.space_after = Pt(6)

    # 2 Signature designated spaces (Left: HOD CSE, Right: T&P In-Charge)
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    tblPr = tbl._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/>'
            f'<w:bottom w:val="none"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="none"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

    cell_left = tbl.cell(0, 0)
    cell_right = tbl.cell(0, 1)
    cell_left.width = Inches(3.0)
    cell_right.width = Inches(3.0)

    # Left: HOD CSE
    p_l = cell_left.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l.paragraph_format.line_spacing = 1.3
    p_l.paragraph_format.space_before = Pt(0)
    p_l.paragraph_format.space_after = Pt(0)
    r_l1 = p_l.add_run("Signature\n\n___________________________\n")
    r_l1.font.name = 'Times New Roman'
    r_l1.font.size = Pt(12)
    r_l1.font.bold = True
    r_l2 = p_l.add_run("Dr. OmPrakash Barapatre\n")
    r_l2.font.name = 'Times New Roman'
    r_l2.font.size = Pt(12)
    r_l2.font.bold = True
    r_l3 = p_l.add_run("HOD (CSE)\nDepartment of Computer Science & Engineering")
    r_l3.font.name = 'Times New Roman'
    r_l3.font.size = Pt(11)
    r_l3.font.bold = False

    # Right: T&P In-Charge
    p_r = cell_right.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.line_spacing = 1.3
    p_r.paragraph_format.space_before = Pt(0)
    p_r.paragraph_format.space_after = Pt(0)
    r_r1 = p_r.add_run("Signature\n\n___________________________\n")
    r_r1.font.name = 'Times New Roman'
    r_r1.font.size = Pt(12)
    r_r1.font.bold = True
    r_r2 = p_r.add_run("Prof. Aparna Pandey\n")
    r_r2.font.name = 'Times New Roman'
    r_r2.font.size = Pt(12)
    r_r2.font.bold = True
    r_r3 = p_r.add_run("T&P In-Charge (CSE)\nDepartment of Computer Science & Engineering")
    r_r3.font.name = 'Times New Roman'
    r_r3.font.size = Pt(11)
    r_r3.font.bold = False

def build_acknowledgments(doc, add_heading_chapter, add_body_p):
    add_heading_chapter(doc, "", "ACKNOWLEDGMENTS")
    
    add_body_p(doc, "I would like to express my deepest gratitude and sincere appreciation to my vocational training supervisor, Dr. Anurag Singh, Associate Professor at IIIT Naya Raipur, for his exceptional guidance, constant technical inspiration, and rigorous scholarly critique throughout the duration of this research. His extensive mastery of biomedical signal processing, machine learning theory, and statistical modeling provided the intellectual foundation that transformed an ambitious vision of non-contact physiological sensing into a clinically sound, functional reality.")
    
    add_body_p(doc, "I extend my sincere thanks to the administration, faculty, and research staff at IIIT NAYA RAIPUR for fostering a world-class, intellectually stimulating environment and granting access to specialized high-performance computational infrastructure.")
    
    add_body_p(doc, "I am profoundly thankful to Prof. OmPrakash Barapatre, Head of the Department of Computer Science & Engineering at Bhilai Institute of Technology (BIT), Raipur, for his continuous encouragement, academic leadership, and administrative support in facilitating our participation in advanced vocational research.")
    
    add_body_p(doc, "Finally, I am indebted to my parents, family members, and colleagues for their constant moral support, patience, and motivation during intensive development phases.")
    
    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(24)
    r = p_sig.add_run("Vedang Bhatt\nB.Tech. Computer Science & Engineering\nBhilai Institute of Technology, Raipur")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True

def build_abstract(doc, add_heading_chapter, add_body_p):
    add_heading_chapter(doc, "", "ABSTRACT")
    
    add_body_p(doc, "Hypertension represents a leading global risk factor for cardiovascular diseases, stroke, and premature mortality, affecting over 1.28 billion adults worldwide. Traditional arterial blood pressure (BP) assessment relies on inflatable pneumatic cuffs, which provide only intermittent, reactive readings and introduce substantial physical disruption that precludes continuous nocturnal monitoring. While contact photoplethysmography (cPPG) wearables have emerged as alternatives, they suffer from sensor detachment, cutaneous irritation, and motion susceptibility. Contactless remote photoplethysmography (rPPG) via standard RGB cameras offers a revolutionary, unobtrusive paradigm for ubiquitous cardiovascular tracking, yet existing optical BP frameworks suffer from severe signal degradation, quantization noise floors, and catastrophic regression-to-the-mean ('template collapse').")
    
    add_body_p(doc, "In this work, we present LuminaBP, an end-to-end, clinically compliant machine learning and deep sequential modeling framework for non-invasive, continuous blood pressure estimation from facial video streams. The proposed system integrates an engineered optical-hemodynamic acquisition pipeline with a novel decoupled neural architecture (MODEL-06-SepHead). The optical pipeline employs sensor-level exposure and white-balance locking, 468-point MediaPipe facial mesh tracking across bilateral malar and upper forehead microvascular regions of interest (ROIs), Plane-Orthogonal-to-Skin (POS) chrominance projection, and adaptive Savitzky-Golay polynomial smoothing to suppress high-frequency quantization noise while strictly preserving subtle dicrotic notch morphology.")
    
    add_body_p(doc, "The deep learning engine extracts spatial and morphological features via a multi-scale 1D Residual Convolutional backbone, captures temporal pulsatile dynamics using Bidirectional Gated Recurrent Units (BiGRU) augmented with Multi-Head Self-Attention (MHSA), and predicts Systolic Blood Pressure (SBP) and Diastolic Blood Pressure (DBP) through mathematically decoupled regression heads to resolve physiological gradient conflicts.")
    
    add_body_p(doc, "Rigorous experimental validation was conducted on the gated MCD dataset (17,943 valid 10-second windows across 599 subjects) under a strict, leak-free 100% subject-level split protocol (419 Train / 90 Val / 90 Test). Experimental results demonstrate that LuminaBP achieves an unprecedented Diastolic BP Mean Absolute Error (MAE) of 5.91 mmHg (RMSE = 8.54 mmHg, Pearson r = 0.355), comfortably satisfying the stringent ISO/AAMI SP10 clinical threshold (MAE <= 8.0 mmHg). For Systolic BP, the model achieves an MAE of 10.12 mmHg (RMSE = 14.58 mmHg, Pearson r = 0.388), outperforming conventional LSTM and monolithic CNN baselines. The entire pipeline is optimized for edge deployment on mobile Android hardware via 8-bit quantized TensorFlow Lite, establishing a robust, contactless digital biomarker platform for next-generation cardiovascular diagnostics.")
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(8)
    r_k1 = p_kw.add_run("Keywords: ")
    r_k1.font.name = 'Times New Roman'
    r_k1.font.size = Pt(11)
    r_k1.font.bold = True
    r_k2 = p_kw.add_run("Remote Photoplethysmography (rPPG), Cuffless Blood Pressure Estimation, Deep Learning, LuminaBP, MODEL-06-SepHead, Savitzky-Golay Denoising, ISO/AAMI SP10 Compliance, Mobile Health.")
    r_k2.font.name = 'Times New Roman'
    r_k2.font.size = Pt(11)
    r_k2.font.italic = True
