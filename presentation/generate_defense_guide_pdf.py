r"""
generate_defense_guide_pdf.py
=============================
Compiles PRESENTER_DEFENSE_GUIDE.md into a high-quality, publication-grade PDF:
'presentation/PRESENTER_DEFENSE_GUIDE.pdf'
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

WORKSPACE = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation"
PRESENTATION_DIR = os.path.join(WORKSPACE, "presentation")
OUTPUT_PDF = os.path.join(PRESENTATION_DIR, "PRESENTER_DEFENSE_GUIDE.pdf")


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 11 * 72 - 25, "Presenter's Defense & Technical Cue Sheet — VT 2026 (IIIT-NR & BIT Raipur)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(36, 11 * 72 - 28, 8.5 * 72 - 36, 11 * 72 - 28)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 36, 20, footer_text)
        self.drawString(36, 20, "Confidential — Academic Defense Cue Sheet | Mobile rPPG to BP Estimation")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 28, 8.5 * 72 - 36, 28)

        self.restoreState()


def build_pdf(output_path=OUTPUT_PDF):
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

    # Color Palette: Deep Academic Teal + Warm Gold + Slate
    C_TEAL_DARK   = colors.HexColor("#1B4332")
    C_TEAL_MID    = colors.HexColor("#2D6A4F")
    C_TEAL_BG     = colors.HexColor("#F0FDF4")
    C_GOLD        = colors.HexColor("#B8860B")
    C_GOLD_BG     = colors.HexColor("#FEF9C3")
    C_SLATE_DARK  = colors.HexColor("#0F172A")
    C_SLATE_BODY  = colors.HexColor("#334155")
    C_BORDER      = colors.HexColor("#E2E8F0")
    C_CARD_BG     = colors.HexColor("#F8FAFC")
    C_WHITE       = colors.HexColor("#FFFFFF")
    C_BLUE_DARK   = colors.HexColor("#1E3A8A")
    C_SCRIPT_BG   = colors.HexColor("#F1F5F9")

    # Typography styles
    style_main_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=C_TEAL_DARK,
        alignment=1,
        spaceAfter=3
    )

    style_sub_title = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=C_GOLD,
        alignment=1,
        spaceAfter=8
    )

    style_sec_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=C_TEAL_DARK,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    style_slide_heading = ParagraphStyle(
        'SlideHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=C_BLUE_DARK,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=C_SLATE_BODY,
        spaceAfter=3
    )

    style_body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=C_SLATE_DARK,
        spaceAfter=3
    )

    style_bullet = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.2,
        textColor=C_SLATE_BODY,
        leftIndent=12,
        spaceAfter=2
    )

    style_script = ParagraphStyle(
        'ScriptText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.3,
        leading=11.5,
        textColor=C_SLATE_DARK,
        spaceAfter=0
    )

    style_script_label = ParagraphStyle(
        'ScriptLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.3,
        leading=11,
        textColor=C_TEAL_MID,
        spaceAfter=2
    )

    style_meta_key = ParagraphStyle(
        'MetaKey',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=C_TEAL_DARK
    )

    style_meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_SLATE_BODY
    )

    style_table_header = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=C_WHITE,
        alignment=1
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_SLATE_BODY
    )

    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=C_SLATE_DARK
    )

    style_qa_q = ParagraphStyle(
        'QAQuestion',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=C_TEAL_DARK,
        spaceAfter=2
    )

    style_qa_a = ParagraphStyle(
        'QAAnswer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.5,
        textColor=C_SLATE_BODY
    )

    story = []

    # -------------------------------------------------------------------------
    # HEADER BANNER & METADATA
    # -------------------------------------------------------------------------
    story.append(Paragraph("Presenter's Master Defense & Technical Cue Sheet", style_main_title))
    story.append(Paragraph("Vocational Training (\"AI with Python\" @ IIIT-NR) & Proposed Capstone Presentation", style_sub_title))

    # Metadata Box (Table)
    meta_table_data = [
        [
            Paragraph("<b>Researchers & Presenters:</b>", style_meta_key),
            Paragraph("1. Vedang Bhatt &nbsp;|&nbsp; 2. Anubhav Shrivastav &nbsp;|&nbsp; 3. Aadarsh (4th Sem B.Tech CSE)", style_meta_val)
        ],
        [
            Paragraph("<b>Parent Institution:</b>", style_meta_key),
            Paragraph("Department of Computer Science & Engineering, Bhilai Institute of Technology (BIT), Raipur", style_meta_val)
        ],
        [
            Paragraph("<b>Training Host Institution:</b>", style_meta_key),
            Paragraph("International Institute of Information Technology, Naya Raipur (IIIT-NR) &nbsp;[01/07/2026 – 10/08/2026]", style_meta_val)
        ],
        [
            Paragraph("<b>Mentors & Guides:</b>", style_meta_key),
            Paragraph("<b>VT Mentor:</b> Dr. Anurag Singh (IIIT-NR) &nbsp;&bull;&nbsp; <b>College Mentor:</b> Prof. Aparna Pandey (BIT Raipur)", style_meta_val)
        ],
        [
            Paragraph("<b>Proposed Project Title:</b>", style_meta_key),
            Paragraph("<i>Mobile Remote Photoplethysmography (rPPG) to Cuffless Blood Pressure Estimation</i>", style_meta_val)
        ]
    ]

    meta_table = Table(meta_table_data, colWidths=[1.7 * inch, 5.7 * inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_CARD_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 1: TIME MANAGEMENT MATRIX
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Presentation Time Management Matrix", style_sec_heading))

    time_matrix_data = [
        [
            Paragraph("Format", style_table_header),
            Paragraph("Duration", style_table_header),
            Paragraph("Focus / Key Deliverable", style_table_header),
            Paragraph("Slide Emphasis", style_table_header)
        ],
        [
            Paragraph("<b>VT Defense / Review</b>", style_table_cell_bold),
            Paragraph("12–15 Mins", style_table_cell_bold),
            Paragraph("VT Learnings @ IIIT-NR &rarr; Syllabus Mastery &rarr; Capstone Motivation & Methodology &rarr; Preliminary Findings", style_table_cell),
            Paragraph("Slides 1 through 11", style_table_cell)
        ],
        [
            Paragraph("<b>Executive Overview</b>", style_table_cell_bold),
            Paragraph("8–10 Mins", style_table_cell_bold),
            Paragraph("Training Summary &rarr; Problem Statement &rarr; End-to-End Pipeline &rarr; Expected Outcomes &rarr; Next Steps", style_table_cell),
            Paragraph("Slides 1, 4, 6, 8, 10, 11", style_table_cell)
        ],
        [
            Paragraph("<b>Comprehensive Seminar</b>", style_table_cell_bold),
            Paragraph("20–25 Mins", style_table_cell_bold),
            Paragraph("Mathematical Concepts (Regression, CNN/LSTM, Savitzky-Golay) &rarr; rPPG Pipeline &rarr; Future Roadmap", style_table_cell),
            Paragraph("All Slides + Q&A", style_table_cell)
        ]
    ]

    time_table = Table(time_matrix_data, colWidths=[1.5 * inch, 0.9 * inch, 3.7 * inch, 1.3 * inch])
    time_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_TEAL_DARK),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, C_TEAL_DARK),
        ('INNERGRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_CARD_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(time_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # HELPER TO BUILD SLIDE CUE CARD
    # -------------------------------------------------------------------------
    def make_slide_card(slide_num, title, core_takeaway, script_text, extra_bullets=None, is_demo=False):
        card_content = []

        card_content.append(Paragraph(f"<b>Slide {slide_num}: {title}</b>", style_slide_heading))
        if core_takeaway:
            card_content.append(Paragraph(f"<b>&bull; Core Takeaway:</b> {core_takeaway}", style_bullet))

        if extra_bullets:
            for b_label, b_text in extra_bullets:
                card_content.append(Paragraph(f"<b>&bull; {b_label}</b> {b_text}", style_bullet))

        if script_text:
            # Script Callout Box
            script_table = Table(
                [[
                    Paragraph("<b>[Speaker Script]:</b>", style_script_label),
                    Paragraph(f'"{script_text}"', style_script)
                ]],
                colWidths=[1.1 * inch, 6.1 * inch]
            )
            script_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), C_TEAL_BG if is_demo else C_SCRIPT_BG),
                ('BOX', (0,0), (-1,-1), 1, C_TEAL_MID if is_demo else C_BORDER),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            card_content.append(Spacer(1, 2))
            card_content.append(script_table)

        card_content.append(Spacer(1, 4))
        return KeepTogether(card_content)

    # -------------------------------------------------------------------------
    # SECTION 2: SLIDE-BY-SLIDE NOTES & CUE CARDS
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Slide-by-Slide Speaker Notes & Technical Cue Cards", style_sec_heading))

    # Slide 1
    story.append(make_slide_card(
        1, "Title Slide & Institutional Acknowledgement",
        "Respectfully introduce the student team, express sincere gratitude to VT Mentor Dr. Anurag Singh (IIIT-NR) and College Mentor Prof. Aparna Pandey (BIT Raipur), and introduce the proposed capstone project.",
        "Respected committee members, faculty, and mentors: Good morning. We are 4th-semester Computer Science & Engineering students from Bhilai Institute of Technology, Raipur. Today, we present our Vocational Training report on 'AI with Python', which we completed at IIIT Naya Raipur under the mentorship of Dr. Anurag Singh from 1st July to 10th August 2026, with the kind guidance of our college mentor Prof. Aparna Pandey. We also present our proposed undergraduate capstone project: 'Mobile Remote Photoplethysmography to Cuffless Blood Pressure Estimation', which directly builds upon the mathematical, signal processing, and deep learning foundations we learned during our training."
    ))

    # Slide 2
    story.append(make_slide_card(
        2, "Introduction to the Vocational Training Program",
        "Academic growth from undergraduate classroom theory (4th Sem) to practical AI workflows at IIIT-NR.",
        "The 6-week Vocational Training at IIIT-NR gave us deep exposure to end-to-end Artificial Intelligence with Python. Under the guidance of our mentors, we progressed from foundational scientific computing and classical machine learning to advanced deep learning architectures, digital signal filtering, and modern agentic AI workflows. This hands-on training empowered us to tackle interdisciplinary problems bridging computational algorithms and biomedical data."
    ))

    # Slide 3
    story.append(make_slide_card(
        3, "Training Objectives & Learning Milestones",
        "Five clear learning milestones achieved across data science, machine learning, deep learning, signal filtering, and modern AI.",
        "Our training objectives were structured into five key milestones: First, mastering scientific data manipulation in Python using NumPy, Pandas, and Matplotlib. Second, understanding classical machine learning algorithms, bias-variance tradeoffs, and rigorous cross-validation. Third, building deep neural networks (CNNs, RNNs, LSTMs, and Self-Attention) in TensorFlow. Fourth, exploring signal smoothing algorithms like the Savitzky-Golay filter. And fifth, gaining early exposure to modern AI paradigms including NLP, Embeddings, RAG, LangChain, and Agentic AI tools."
    ))

    # Slide 4
    story.append(make_slide_card(
        4, "Detailed Curriculum & Topics Covered (45 Syllabus Topics)",
        "Clear categorization of the 45 syllabus topics into 4 structured, coherent modules.",
        None,
        extra_bullets=[
            ("Module 1 (Python & Scientific Foundations):", "Python core, NumPy vectorization, Pandas wrangling & preprocessing, Matplotlib visualization."),
            ("Module 2 (Machine Learning & Validation):", "Supervised/Unsupervised paradigms, Linear/Polynomial/Logistic regression, Overfitting, K-Fold CV, Precision/Recall/F1."),
            ("Module 3 (Deep Learning & Architectures):", "TensorFlow graph execution, Activations (Sigmoid, ReLU, SoftMax), Backprop, CNNs, Sequence models (RNN, LSTM), Self-Attention."),
            ("Module 4 (Signal Processing, NLP & Modern AI):", "Savitzky-Golay filter, NLTK, Word2Vec, GloVe, Embeddings, Transformers, RAG, LangChain, Agentic AI, MCP.")
        ]
    ))

    # Slide 5
    story.append(make_slide_card(
        5, "Key Learnings & Bridging Theory to Project",
        "Explain how classroom learning and digital signal smoothing directly inspired our applied capstone project.",
        "Our key takeaway was that raw data in real-world applications is rarely clean. Specifically, understanding the Savitzky-Golay filter for local polynomial smoothing taught us how to denoise physiological signals without distorting their characteristic peaks. Combining this with 1D Convolutions and Recurrent/Attention layers inspired us to ask: can we use a standard smartphone camera to extract optical heart pulses and estimate blood pressure? This question formed the foundation of our proposed project."
    ))

    # Slide 6
    story.append(make_slide_card(
        6, "Proposed Project — Title & Introduction",
        "Clinical motivation around hypertension (1.28B people) and the non-invasive optical smartphone alternative.",
        "Hypertension affects over 1.28 billion people worldwide and is often asymptomatic. While traditional upper-arm cuffs are accurate, they are cumbersome and cannot provide continuous monitoring. Our proposed project explores remote Photoplethysmography (rPPG)—detecting microscopic skin color fluctuations caused by cardiovascular pulsations via commodity smartphone cameras—to non-invasively estimate blood pressure without specialized hardware."
    ))

    # Slide 7
    story.append(make_slide_card(
        7, "Objectives & Scope of Proposed Project",
        "Clear deliverables spanning optical pulse ingestion, signal conditioning, neural modeling, and edge feasibility.",
        None,
        extra_bullets=[
            ("Optical Frontend:", "Front-camera pulse acquisition with Camera2 AE/AWB illumination stabilization."),
            ("ROI & Color Space:", "Facial ROI tracking and POS chrominance projection to eliminate ambient specular reflections."),
            ("Signal Conditioning:", "Digital filtering via Butterworth bandpass [0.75, 3.0 Hz] and Savitzky-Golay polynomial smoothing."),
            ("Neural Modeling:", "Deep sequence regression using TensorFlow (1D-CNN + BiGRU + Multi-Head Self-Attention)."),
            ("Calibration & Edge:", "Single-point calibration for vascular dynamics and edge mobile deployment for on-device privacy.")
        ]
    ))

    # Slide 8
    story.append(make_slide_card(
        8, "Methodology / Approach of Proposed Project",
        "Structured 5-stage pipeline: Camera2 Sensor Lock -> Facial ROI Tracking -> POS Chrominance -> Savitzky-Golay DSP -> Deep Regression.",
        "Our proposed methodology follows a structured five-stage pipeline: First, locking camera sensor parameters to eliminate auto-exposure drift. Second, tracking facial regions to extract average skin pixel channels. Third, applying Plane-Orthogonal-to-Skin (POS) projection to cancel ambient specular reflections. Fourth, smoothing the pulse using Savitzky-Golay and bandpass filtering. And fifth, feeding the conditioned pulse into a deep regression network to estimate Systolic and Diastolic blood pressure."
    ))

    # Slide 9
    story.append(make_slide_card(
        9, "Work Details & Live Demonstration Touchpoint",
        "Detailing MODEL-06-SepHead architecture in TensorFlow and smoothly transitioning to the live smartphone demonstration.",
        "Our neural architecture—MODEL-06-SepHead—combines dual-branch 1D Convolutions for systolic peak extraction with Bidirectional GRU and 4-head Self-Attention for cardiac rhythm modeling, terminating in decoupled heads for SBP and DBP.\n\n[Live Demo Transition]: At this stage, we would like to switch to our smartphone for a brief live demonstration, showcasing real-time Camera2 video acquisition, facial ROI tracking, and on-device pulse waveform visualization in action.",
        is_demo=True
    ))

    # Slide 10
    story.append(make_slide_card(
        10, "Expected Outcomes & Results of Proposed Project Work",
        "Validated empirical results across clinical benchmark datasets: 10.12/5.91 mmHg MAE, 8.9 dB POS SNR, 120 ms latency.",
        "In our exploratory evaluations, our model achieved an MAE of 10.12 mmHg for SBP and 5.91 mmHg for DBP, representing a 6.70 mmHg reduction in error compared to baseline linear models. Furthermore, POS chrominance projection achieved 8.9 dB SNR, and offline batch inference executes in approximately 120 ms on commodity mobile CPUs with zero dropped frames."
    ))

    # Slide 11
    story.append(make_slide_card(
        11, "Conclusion Remarks & Future Scope of Work",
        "Sincere gratitude to mentors at IIIT-NR and BIT Raipur, followed by an outline of upcoming capstone milestones.",
        "In conclusion, our 6-week training at IIIT-NR in 'AI with Python' under the guidance of Dr. Anurag Singh and Prof. Aparna Pandey gave us the theoretical and practical foundation to formulate this capstone project. Moving forward, our roadmap includes clinical testing across diverse Fitzpatrick skin phototypes, mobile NPU hardware acceleration for sub-50ms inference, and multimodal optical sensing. We sincerely thank our mentors and faculty members for their support, and we welcome your questions."
    ))

    story.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # SECTION 3: HUMBLE & PREPARED ANSWERS FOR COMMITTEE QUESTIONS
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Humble & Prepared Answers for Committee Questions", style_sec_heading))

    qa_list = [
        (
            "Q1: \"How does what you learned at IIIT-NR relate to your proposed project?\"",
            "\"At IIIT-NR, we were taught the full spectrum of AI with Python—from data preprocessing with NumPy/Pandas to deep learning architectures in TensorFlow (CNNs, LSTMs, Attention) and digital filtering like Savitzky-Golay. Our proposed project applies these exact principles: we use Python scientific tools for signal wrangling, the Savitzky-Golay filter to smooth optical pulse waves, and CNN/LSTM/Attention networks to regress blood pressure from those waves.\""
        ),
        (
            "Q2: \"Why is digital signal filtering (like Savitzky-Golay) necessary if you are using deep learning?\"",
            "\"While deep neural networks are strong feature extractors, raw camera signals contain high-frequency sensor noise and low-frequency baseline drifts. As we learned during training, quality preprocessing and local polynomial filtering (like Savitzky-Golay) preserve essential peak morphology (such as systolic peaks) while removing out-of-band noise, which substantially eases the neural network's learning burden.\""
        ),
        (
            "Q3: \"Can smartphone cameras accurately estimate blood pressure without any cuff?\"",
            "\"Camera rPPG directly measures relative optical blood volume pulses, not absolute pressure in mmHg. Because arterial stiffness and vascular geometry vary across individuals, a completely uncalibrated model tends to regress towards the dataset average. Therefore, our proposal incorporates single-point calibration—using an initial reference reading to anchor personal baseline values—making continuous tracking much more reliable.\""
        ),
        (
            "Q4: \"What are the limitations of your current student prototype?\"",
            "\"Currently, our work is in the prototype and research formulation stage. Key limitations include sensitivity to sudden head movement, variations under low ambient illumination, and the need for testing across broader datasets with diverse skin tones. Addressing these challenges forms our primary roadmap for the upcoming capstone semesters.\""
        )
    ]

    for q_text, a_text in qa_list:
        qa_table = Table(
            [
                [Paragraph(f"<b>{q_text}</b>", style_qa_q)],
                [Paragraph(f"<b>Answer:</b> {a_text}", style_qa_a)]
            ],
            colWidths=[7.4 * inch]
        )
        qa_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_CARD_BG),
            ('BOX', (0,0), (-1,-1), 1, C_BORDER),
            ('LINEBEFORE', (0,0), (0,-1), 3, C_GOLD),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(KeepTogether([qa_table, Spacer(1, 4)]))

    # Build PDF with dynamic page numbering
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Presenter Defense Guide PDF compiled successfully: {output_path}")


if __name__ == "__main__":
    build_pdf()
