r"""
generate_redesigned_deck.py

Senior-Grade python-pptx Architecture for 'Modern Minimalist Academic Studio' Deck.
Implements:
  - Clean Solid White Canvas (#FFFFFF)
  - Modular Card UI with hairline slate borders (#E2E8F0) and soft fills (#F8FAFC)
  - Clear Visual Hierarchy (Deep Navy #0F172A titles, Slate #334155 body, Royal Blue #1D4ED8 & Warm Amber #D97706 accents)
  - Preserved BIT Raipur Logo from Sample PPT
  - Full 45-topic syllabus from Topics Covered.txt (IIIT-NR, AI with Python, 01/07/2026 to 10/08/2026, 4th Sem)
  - Mentors: Dr. Anurag Singh (IIIT-NR) & Prof. Aparna Pandey (BIT Raipur)
  - Dedicated "Live Mobile Demonstration" switch touchpoint on Slide 9/10
  - Zero image distortion / exact aspect ratio fitting

Outputs:
  - presentation/VT_2026_rPPG_to_BP_Estimation.pptx
  - presentation/VT_2026_Redesigned_Deck.pptx
  - C:\Users\simpl\Downloads\Sample PPT _VT 2026.pptx
"""

import os
from PIL import Image
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# =============================================================================
# 1. COLOR SYSTEM & DESIGN TOKENS (ACADEMIC STUDIO LIGHT)
# =============================================================================
COLOR_BG_WHITE       = RGBColor(255, 255, 255) # #FFFFFF Pure White
COLOR_CARD_FILL      = RGBColor(248, 250, 252) # #F8FAFC Soft Slate 50
COLOR_CARD_HIGHLIGHT = RGBColor(241, 245, 249) # #F1F5F9 Slate 100
COLOR_CARD_BORDER    = RGBColor(226, 232, 240) # #E2E8F0 Hairline Border
COLOR_BORDER_STRONG  = RGBColor(203, 213, 225) # #CBD5E1 Medium Border

COLOR_TITLE_NAVY     = RGBColor(15, 23, 42)    # #0F172A Deep Navy
COLOR_TEXT_PRIMARY   = RGBColor(30, 41, 59)    # #1E293B Slate 800
COLOR_TEXT_MUTED     = RGBColor(71, 85, 105)   # #475569 Slate 600
COLOR_TEXT_DIM       = RGBColor(100, 116, 139) # #64748B Slate 500

COLOR_BLUE_ACCENT    = RGBColor(29, 78, 216)   # #1D4ED8 Royal Blue
COLOR_CYAN_ACCENT    = RGBColor(2, 132, 199)   # #0284C7 Medical Cyan
COLOR_AMBER_ACCENT   = RGBColor(217, 119, 6)   # #D97706 Warm Amber
COLOR_EMERALD_ACCENT = RGBColor(5, 150, 105)   # #059669 Emerald Green
COLOR_PURPLE_ACCENT  = RGBColor(124, 58, 237)  # #7C3AED Royal Purple

FONT_HEADING = "Arial"
FONT_BODY    = "Calibri"

SLIDE_WIDTH_INCHES  = 13.333
SLIDE_HEIGHT_INCHES = 7.500

WORKSPACE_DIR = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation"
ASSETS_DIR    = os.path.join(WORKSPACE_DIR, "presentation", "assets")
FULL_OUTPUT   = os.path.join(WORKSPACE_DIR, "presentation", "VT_2026_rPPG_to_BP_Estimation.pptx")
REDESIGN_OUT  = os.path.join(WORKSPACE_DIR, "presentation", "VT_2026_Redesigned_Deck.pptx")
DOWNLOADS_OUT = r"C:\Users\simpl\Downloads\Sample PPT _VT 2026.pptx"

# =============================================================================
# 2. CORE HELPER FUNCTIONS
# =============================================================================

def create_presentation():
    """Initializes a 16:9 widescreen presentation."""
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
    prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)
    return prs

def apply_slide_bg(slide):
    """Sets a clean solid white background."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG_WHITE

def add_header(slide, title, category=None):
    """
    Standardized professional header band:
      - Category / Breadcrumb pill (Royal Blue or Amber)
      - Clear bold Navy Title (21pt)
      - Subtle 1.5pt accent underline divider
    """
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.95))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    if category:
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_HEADING
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_BLUE_ACCENT
        p_cat.space_after = Pt(2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]

    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TITLE_NAVY
    p_title.alignment = PP_ALIGN.LEFT

    # Subtle horizontal divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BLUE_ACCENT
    line.line.color.rgb = COLOR_BLUE_ACCENT
    line.line.width = Pt(0)

def add_card(slide, left, top, width, height, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER, border_width=Pt(1)):
    """Creates a clean rounded card container with crisp borders."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = border_width
    return card

def add_image_fit(slide, img_path, box_left, box_top, box_width, box_height):
    """Places an image preserving exact aspect ratio centered in the target bounding box."""
    if not os.path.exists(img_path):
        print(f"Warning: Image not found at {img_path}")
        return None

    with Image.open(img_path) as im:
        img_w, img_h = im.size

    img_aspect = img_w / img_h
    b_left = float(box_left)
    b_top  = float(box_top)
    b_w    = float(box_width)
    b_h    = float(box_height)
    box_aspect = b_w / b_h

    if img_aspect > box_aspect:
        final_w = b_w
        final_h = b_w / img_aspect
        final_left = b_left
        final_top = b_top + (b_h - final_h) / 2.0
    else:
        final_h = b_h
        final_w = b_h * img_aspect
        final_top = b_top
        final_left = b_left + (b_w - final_w) / 2.0

    return slide.shapes.add_picture(img_path, int(final_left), int(final_top), int(final_w), int(final_h))

# =============================================================================
# 3. HIGH-EFFORT MODULAR SLIDE BUILDERS
# =============================================================================

def build_slide_1_title(prs):
    """Slide 1: Title Slide & Institutional Acknowledgement with BIT Logo."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)

    # Official BIT Raipur Logo at Top-Left
    logo_path = os.path.join(ASSETS_DIR, "image1.jpeg")
    if os.path.exists(logo_path):
        add_image_fit(slide, logo_path, Inches(0.8), Inches(0.4), Inches(1.35), Inches(1.35))

    # Top Tag / Department Breadcrumb
    tag_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.45), Inches(11.333), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "A PRESENTATION ON VOCATIONAL TRAINING & PROPOSED CAPSTONE PROJECT"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag.alignment = PP_ALIGN.CENTER

    # Main Project Title
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.80), Inches(11.333), Inches(1.35))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = "Mobile Remote Photoplethysmography to\nCuffless Blood Pressure Estimation"
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(25)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TITLE_NAVY
    p_title.alignment = PP_ALIGN.CENTER

    # Accent Underline
    line_w = Inches(5.0)
    line_left = (Inches(SLIDE_WIDTH_INCHES) - line_w) / 2
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, line_left, Inches(2.25), line_w, Pt(2))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_BLUE_ACCENT
    line.line.color.rgb = COLOR_BLUE_ACCENT
    line.line.width = Pt(0)

    # Subtitle: Training Details
    sub_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.35), Inches(11.333), Inches(0.50))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Vocational Training on 'AI with Python' undergone at IIIT Naya Raipur (01/07/2026 to 10/08/2026)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = COLOR_TEXT_MUTED
    p_sub.alignment = PP_ALIGN.CENTER

    # Center Metadata Container (Presenters, Mentors, College)
    meta_container = add_card(slide, Inches(1.0), Inches(2.95), Inches(11.333), Inches(2.05), fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)
    
    meta_tb = slide.shapes.add_textbox(Inches(1.2), Inches(3.05), Inches(10.933), Inches(1.85))
    tf_meta = meta_tb.text_frame
    tf_meta.word_wrap = True

    p_p = tf_meta.paragraphs[0]
    p_p.text = "Presented By:   Vedang Bhatt (4th Sem)   •   Anubhav Shrivastav (4th Sem)   •   Aadarsh (4th Sem)"
    p_p.font.name = FONT_HEADING
    p_p.font.size = Pt(12)
    p_p.font.bold = True
    p_p.font.color.rgb = COLOR_TEXT_PRIMARY
    p_p.alignment = PP_ALIGN.CENTER
    p_p.space_after = Pt(4)

    p_m = tf_meta.add_paragraph()
    p_m.text = "Mentors:   VT Mentor: Dr. Anurag Singh (IIIT-NR)   •   College Mentor: Prof. Aparna Pandey (BIT Raipur)"
    p_m.font.name = FONT_HEADING
    p_m.font.size = Pt(11.5)
    p_m.font.bold = True
    p_m.font.color.rgb = COLOR_AMBER_ACCENT
    p_m.alignment = PP_ALIGN.CENTER
    p_m.space_after = Pt(4)

    p_c = tf_meta.add_paragraph()
    p_c.text = "Department of Computer Science & Engineering, Bhilai Institute of Technology, Raipur"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(11.5)
    p_c.font.bold = True
    p_c.font.color.rgb = COLOR_BLUE_ACCENT
    p_c.alignment = PP_ALIGN.CENTER

    # 3 High-Effort Feature Cards at Bottom
    kpi_w = Inches(3.64)
    kpi_gap = Inches(0.20)
    kpi_top = Inches(5.20)
    kpi_h = Inches(1.75)

    kpi_data = [
        ("AI WITH PYTHON", "IIIT-NR Vocational Training", "Comprehensive 6-week program covering 45 progressive topics from data preprocessing to agentic systems.", COLOR_BLUE_ACCENT),
        ("APPLIED DSP & DL", "Signal Filtering to Neural Regressors", "Savitzky-Golay polynomial smoothing combined with 1D-CNN, BiGRU & Self-Attention sequence networks.", COLOR_AMBER_ACCENT),
        ("CAPSTONE PROPOSAL", "Contactless Cardiovascular Screening", "Smartphone camera rPPG pipeline for non-invasive, privacy-native continuous blood pressure monitoring.", COLOR_EMERALD_ACCENT)
    ]

    for i, (tag, title, desc, accent) in enumerate(kpi_data):
        c_left = Inches(1.0) + i * (kpi_w + kpi_gap)
        add_card(slide, c_left, kpi_top, kpi_w, kpi_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)
        
        # Left Accent Border Strip
        accent_strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, kpi_top, Inches(0.08), kpi_h)
        accent_strip.fill.solid()
        accent_strip.fill.fore_color.rgb = accent
        accent_strip.line.color.rgb = accent
        accent_strip.line.width = Pt(0)

        tb = slide.shapes.add_textbox(c_left + Inches(0.18), kpi_top + Inches(0.12), kpi_w - Inches(0.28), kpi_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = tag
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = accent
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TITLE_NAVY
        p2.space_after = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_2_intro(prs):
    """Slide 2: Introduction about the Training Undergone."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 2: Introduction about the training undergone", "Vocational Training Overview @ IIIT-NR")

    card_w = Inches(3.77)
    card_gap = Inches(0.20)
    card_top = Inches(1.65)
    card_h = Inches(5.35)

    cards = [
        {
            "tag": "01 • INSTITUTIONAL EXPOSURE",
            "title": "Academic Training at IIIT-NR",
            "color": COLOR_BLUE_ACCENT,
            "bullets": [
                ("Host Institution:", "International Institute of Information Technology, Naya Raipur (IIIT-NR)."),
                ("Course & Duration:", "'AI with Python' intensive training from 01/07/2026 to 10/08/2026."),
                ("Academic Standing:", "Attended during 4th Semester (B. Tech. Computer Science & Engineering)."),
                ("Core Motivation:", "Transitioning from classroom theory to practical, hands-on computational AI workflows under expert mentorship.")
            ]
        },
        {
            "tag": "02 • PROGRESSIVE CURRICULUM",
            "title": "End-to-End Technical Journey",
            "color": COLOR_AMBER_ACCENT,
            "bullets": [
                ("Scientific Foundations:", "Vectorized computing with NumPy, tabular wrangling with Pandas, and plotting with Matplotlib."),
                ("Machine Learning Rigor:", "Supervised/Unsupervised models, bias-variance tradeoffs, and K-Fold cross-validation."),
                ("Deep Learning:", "TensorFlow computation graphs, CNN spatial convolutions, and RNN/LSTM sequential modeling."),
                ("Signal Conditioning:", "Digital filtering with Savitzky-Golay for noise suppression without peak deformation.")
            ]
        },
        {
            "tag": "03 • APPLIED PROBLEM SOLVING",
            "title": "Modern AI & Project Bridge",
            "color": COLOR_EMERALD_ACCENT,
            "bullets": [
                ("Emerging Paradigms:", "NLP with NLTK, Word2Vec, GloVe, Contextual Embeddings, and Transformer Encoders."),
                ("Modern Orchestration:", "RAG architectures, open-model fine-tuning, LangChain, and Agentic AI tools / MCP."),
                ("Project Formulation:", "Applying Python scientific libraries and signal filtering to real-world biomedical pulse estimation."),
                ("Ethical Focus:", "Understanding data privacy, edge execution, and honest clinical limitations.")
            ]
        }
    ]

    for i, c in enumerate(cards):
        c_left = Inches(0.8) + i * (card_w + card_gap)
        add_card(slide, c_left, card_top, card_w, card_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

        # Top Accent Strip
        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, card_top, card_w, Inches(0.08))
        strip.fill.solid()
        strip.fill.fore_color.rgb = c["color"]
        strip.line.color.rgb = c["color"]
        strip.line.width = Pt(0)

        tb = slide.shapes.add_textbox(c_left + Inches(0.22), card_top + Inches(0.18), card_w - Inches(0.44), card_h - Inches(0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        p_tag = tf.paragraphs[0]
        p_tag.text = c["tag"]
        p_tag.font.name = FONT_HEADING
        p_tag.font.size = Pt(9)
        p_tag.font.bold = True
        p_tag.font.color.rgb = c["color"]
        p_tag.space_after = Pt(3)

        p_title = tf.add_paragraph()
        p_title.text = c["title"]
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_TITLE_NAVY
        p_title.space_after = Pt(10)

        for label, desc in c["bullets"]:
            pb = tf.add_paragraph()
            pb.space_after = Pt(8)
            
            run_lbl = pb.add_run()
            run_lbl.text = f"• {label} "
            run_lbl.font.name = FONT_HEADING
            run_lbl.font.size = Pt(10)
            run_lbl.font.bold = True
            run_lbl.font.color.rgb = COLOR_TEXT_PRIMARY

            run_desc = pb.add_run()
            run_desc.text = desc
            run_desc.font.name = FONT_BODY
            run_desc.font.size = Pt(9.5)
            run_desc.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_3_objectives(prs):
    """Slide 3: Training Objectives."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 3: Training Objectives", "Core Pedagogical Goals @ IIIT-NR")

    card_w = Inches(11.733)
    card_h = Inches(0.92)
    card_gap = Inches(0.14)
    start_top = Inches(1.65)

    objectives = [
        ("01", "Python & Scientific Data Foundations", "Master vectorized matrix operations with NumPy, tabular data manipulation with Pandas, and feature visualization with Matplotlib.", COLOR_BLUE_ACCENT),
        ("02", "Machine Learning & Generalization Rigor", "Understand supervised/unsupervised paradigms (linear, polynomial, logistic), bias-variance dynamics, L1/L2 regularization, and K-Fold cross-validation.", COLOR_CYAN_ACCENT),
        ("03", "Deep Learning & Sequential Architectures", "Build computational graphs in TensorFlow—mastering activations (Sigmoid, ReLU, SoftMax), backpropagation, CNNs, and recurrent models (RNN, LSTM, Self-Attention).", COLOR_AMBER_ACCENT),
        ("04", "Digital Signal Conditioning & Mathematics", "Implement Savitzky-Golay digital polynomial filters for smoothing continuous waveforms without peak distortion; explore vector cosine similarity.", COLOR_PURPLE_ACCENT),
        ("05", "Natural Language Processing & Agentic AI", "Gain introductory exposure to Word2Vec, GloVe, Transformer encoders, RAG architecture, LangChain orchestration, and Agentic AI tools / MCP.", COLOR_EMERALD_ACCENT)
    ]

    for i, (num, title, desc, color) in enumerate(objectives):
        top_pos = start_top + i * (card_h + card_gap)
        add_card(slide, Inches(0.8), top_pos, card_w, card_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

        # Left Number Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), top_pos + Inches(0.14), Inches(0.65), Inches(0.64))
        badge.fill.solid()
        badge.fill.fore_color.rgb = color
        badge.line.color.rgb = color
        badge.line.width = Pt(0)
        
        btf = badge.text_frame
        btf.word_wrap = False
        bp = btf.paragraphs[0]
        bp.text = num
        bp.font.name = FONT_HEADING
        bp.font.size = Pt(13)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_BG_WHITE
        bp.alignment = PP_ALIGN.CENTER

        # Content Textbox
        tb = slide.shapes.add_textbox(Inches(1.75), top_pos + Inches(0.10), Inches(10.6), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TITLE_NAVY
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_4_curriculum(prs):
    """Slide 4: Training Modules / Topics Covered (45 Topics)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 4: Training Modules / Topics Covered", "Comprehensive 45-Topic Syllabus @ IIIT-NR")

    col_w = Inches(2.22)
    col_gap = Inches(0.15)
    col_top = Inches(1.65)
    col_h = Inches(5.35)

    modules = [
        {
            "mod": "MOD 1",
            "title": "Python & Data",
            "color": COLOR_BLUE_ACCENT,
            "topics": [
                "Python basics & syntax",
                "NumPy library array ops",
                "Pandas library wrangling",
                "Matplotlib visualizations",
                "Data preprocessing pipelines",
                "Feature scaling & normalization"
            ]
        },
        {
            "mod": "MOD 2",
            "title": "Machine Learning",
            "color": COLOR_CYAN_ACCENT,
            "topics": [
                "Supervised & Unsupervised",
                "Semi-Supervised & RL",
                "Linear & Polynomial reg.",
                "Logistic regression",
                "Underfitting / Overfitting",
                "Regularisation (L1 / L2)",
                "K-fold cross-validation",
                "Metrics: Acc, Prec, Rec, F1"
            ]
        },
        {
            "mod": "MOD 3",
            "title": "Deep Learning",
            "color": COLOR_AMBER_ACCENT,
            "topics": [
                "TensorFlow ecosystem",
                "Computational graphs",
                "Backpropagation algorithm",
                "Activations: Sigmoid, ReLU, Tanh, SoftMax",
                "Layers: Conv, Pool, Dense",
                "CNN architectures",
                "DNN, RNN & LSTM models",
                "Self-Attention primitives"
            ]
        },
        {
            "mod": "MOD 4",
            "title": "Signal & NLP",
            "color": COLOR_PURPLE_ACCENT,
            "topics": [
                "Savitzky-Golay digital filter",
                "NLP foundations & NLTK",
                "Word-to-vec representations",
                "GloVe embeddings",
                "Sequence encoders",
                "Contextual embeddings",
                "Vector Cosine Similarity"
            ]
        },
        {
            "mod": "MOD 5",
            "title": "GenAI & Agents",
            "color": COLOR_EMERALD_ACCENT,
            "topics": [
                "Transformer architectures",
                "Tokens & Tokenization",
                "Large Language Models",
                "Fine-tuning open models",
                "RAG system architecture",
                "LangChain orchestration",
                "Agentic AI & tool calling",
                "MCP (Model Context Protocol)"
            ]
        }
    ]

    for i, m in enumerate(modules):
        c_left = Inches(0.8) + i * (col_w + col_gap)
        add_card(slide, c_left, col_top, col_w, col_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

        # Header Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Inches(0.12), col_top + Inches(0.12), col_w - Inches(0.24), Inches(0.48))
        pill.fill.solid()
        pill.fill.fore_color.rgb = m["color"]
        pill.line.color.rgb = m["color"]
        pill.line.width = Pt(0)

        ptf = pill.text_frame
        ptf.word_wrap = True
        pp1 = ptf.paragraphs[0]
        pp1.text = m["mod"]
        pp1.font.name = FONT_HEADING
        pp1.font.size = Pt(8.5)
        pp1.font.bold = True
        pp1.font.color.rgb = COLOR_BG_WHITE
        pp1.alignment = PP_ALIGN.CENTER

        pp2 = ptf.add_paragraph()
        pp2.text = m["title"]
        pp2.font.name = FONT_HEADING
        pp2.font.size = Pt(9.5)
        pp2.font.bold = True
        pp2.font.color.rgb = COLOR_BG_WHITE
        pp2.alignment = PP_ALIGN.CENTER

        # Bullet List Textbox
        tb = slide.shapes.add_textbox(c_left + Inches(0.10), col_top + Inches(0.68), col_w - Inches(0.20), col_h - Inches(0.76))
        tf = tb.text_frame
        tf.word_wrap = True

        for idx, t in enumerate(m["topics"]):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.text = f"• {t}"
            p.font.name = FONT_BODY
            p.font.size = Pt(8.5)
            p.font.color.rgb = COLOR_TEXT_PRIMARY
            p.space_after = Pt(3.5)

    return slide

def build_slide_5_learnings(prs):
    """Slide 5: Key Learnings & Bridging Theory to Project."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 5: Key Learnings", "Practical Insights Gained Under Mentorship")

    card_w = Inches(5.76)
    card_h = Inches(2.55)
    card_gap = Inches(0.20)
    top_r1 = Inches(1.65)
    top_r2 = top_r1 + card_h + card_gap

    learnings = [
        (
            "DATA PREPROCESSING & VALIDATION",
            "1. Real-World Signals Require Rigorous Preprocessing",
            "Real-world data—whether tabular, audio, or physiological—carries severe baseline wander and sensor noise. Standardizing feature distributions, robust encoding, and using K-fold validation are indispensable before training any deep neural network.",
            COLOR_BLUE_ACCENT,
            Inches(0.8),
            top_r1
        ),
        (
            "SIGNAL FILTERING & SMOOTHING",
            "2. Digital Smoothing Preserves Critical Peak Morphology",
            "Learning digital signal smoothing techniques like the Savitzky-Golay filter demonstrated how local polynomial regression effectively removes high-frequency noise while preserving vital systolic/diastolic peak extrema without distorting waveform shape.",
            COLOR_AMBER_ACCENT,
            Inches(0.8) + card_w + card_gap,
            top_r1
        ),
        (
            "NEURAL ARCHITECTURE DESIGN",
            "3. Synergy of Convolutional & Recurrent / Attention Layers",
            "Understanding CNNs and LSTMs in TensorFlow revealed that combining 1D convolutions (for localized morphological feature extraction) with recurrent and self-attention layers (for temporal cardiac periodicity) provides superior time-series representation.",
            COLOR_PURPLE_ACCENT,
            Inches(0.8),
            top_r2
        ),
        (
            "CAPSTONE FORMULATION",
            "4. Applied Exploration: Optical Blood Pressure Estimation",
            "Guided by our coursework in Python, signal processing, and deep neural models, we formulated our undergraduate capstone project: extracting transcutaneous optical pulse signals from smartphone cameras to explore cuffless blood pressure estimation.",
            COLOR_EMERALD_ACCENT,
            Inches(0.8) + card_w + card_gap,
            top_r2
        )
    ]

    for tag, title, desc, color, left, top in learnings:
        add_card(slide, left, top, card_w, card_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

        # Accent Corner Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.22), top + Inches(0.18), Inches(2.6), Inches(0.30))
        pill.fill.solid()
        pill.fill.fore_color.rgb = color
        pill.line.color.rgb = color
        pill.line.width = Pt(0)
        
        ptf = pill.text_frame
        pp = ptf.paragraphs[0]
        pp.text = tag
        pp.font.name = FONT_HEADING
        pp.font.size = Pt(8)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_BG_WHITE
        pp.alignment = PP_ALIGN.CENTER

        tb = slide.shapes.add_textbox(left + Inches(0.22), top + Inches(0.55), card_w - Inches(0.44), card_h - Inches(0.65))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TITLE_NAVY
        p1.space_after = Pt(5)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_6_proposal(prs):
    """Slide 6: Proposed Project Title & its Introduction."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 6: Proposed Project Title & its Introduction", "Proposed Capstone Project Definition")

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Card: Problem & Clinical Motivation
    add_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.20), split_w - Inches(0.50), split_h - Inches(0.40))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "PROPOSED CAPSTONE PROJECT TITLE"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag.space_after = Pt(2)

    p_t = tf_l.add_paragraph()
    p_t.text = "Mobile Remote Photoplethysmography (rPPG) to Cuffless Blood Pressure Estimation"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TITLE_NAVY
    p_t.space_after = Pt(10)

    bullets = [
        ("Global Clinical Burden:", "Hypertension affects over 1.28 billion adults globally and is a primary risk factor for stroke and cardiovascular disease."),
        ("Limitations of Arm Cuffs:", "Standard occlusive arm cuffs are intermittent, bulky, uncomfortable, and disrupt sleep during 24-hour ambulatory monitoring."),
        ("White-Coat Effect:", "In-clinic cuff inflation often induces transient acute stress, leading to false-positive hypertension readings."),
        ("Proposed Contactless Solution:", "Using commodity smartphone RGB front cameras to detect microscopic facial color variations caused by blood volume pulses, estimating continuous blood pressure non-invasively.")
    ]

    for label, desc in bullets:
        pb = tf_l.add_paragraph()
        pb.space_after = Pt(8)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(10)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_PRIMARY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Diagram
    right_left = Inches(0.8) + split_w + split_gap
    add_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_BG_WHITE, border_color=COLOR_CARD_BORDER)

    img_path = os.path.join(ASSETS_DIR, "fig_windkessel_damping.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    # Caption
    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 1: Transcutaneous Optical Absorption & Hemodynamic Waveform Dynamics"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9.5)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_7_objectives_project(prs):
    """Slide 7: Objectives of the Proposed Project."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 7: Objectives of the Proposed Project", "System Specifications & Engineering Deliverables")

    card_w = Inches(11.733)
    card_h = Inches(0.92)
    card_gap = Inches(0.14)
    start_top = Inches(1.65)

    deliverables = [
        ("01", "Optical Pulse Extraction via Smartphone Camera", "Capture facial video at 30 FPS using locked camera exposure/white balance; isolate forehead skin microvascular ROIs using facial landmarks and POS chrominance projection.", COLOR_BLUE_ACCENT),
        ("02", "Physiological Signal Denoising & Conditioning", "Standardize variable frame rates to a uniform 125 Hz grid via PCHIP interpolation and apply Savitzky-Golay polynomial smoothing + Butterworth bandpass (0.75–2.5 Hz).", COLOR_CYAN_ACCENT),
        ("03", "Deep Neural Sequence Regression", "Develop a hybrid deep architecture (1D-CNN feature extraction + BiGRU sequence modeling + Self-Attention) in TensorFlow with decoupled linear heads for SBP and DBP.", COLOR_AMBER_ACCENT),
        ("04", "Single-Point Personal Calibration Study", "Investigate single-point baseline calibration to anchor individual vascular tone and arterial stiffness, overcoming physiological 'template collapse'.", COLOR_PURPLE_ACCENT),
        ("05", "Privacy-Preserving On-Device Mobile Execution", "Optimize model inference for lightweight Android execution (using TFLite quantization), ensuring 100% on-device privacy with zero cloud transmission.", COLOR_EMERALD_ACCENT)
    ]

    for i, (num, title, desc, color) in enumerate(deliverables):
        top_pos = start_top + i * (card_h + card_gap)
        add_card(slide, Inches(0.8), top_pos, card_w, card_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), top_pos + Inches(0.14), Inches(0.65), Inches(0.64))
        badge.fill.solid()
        badge.fill.fore_color.rgb = color
        badge.line.color.rgb = color
        badge.line.width = Pt(0)
        
        btf = badge.text_frame
        btf.word_wrap = False
        bp = btf.paragraphs[0]
        bp.text = num
        bp.font.name = FONT_HEADING
        bp.font.size = Pt(13)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_BG_WHITE
        bp.alignment = PP_ALIGN.CENTER

        tb = slide.shapes.add_textbox(Inches(1.75), top_pos + Inches(0.10), Inches(10.6), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TITLE_NAVY
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_8_methodology(prs):
    """Slide 8: Methodology / Approach of the Proposed Project."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 9: Methodology / Approach of the Proposed Project", "End-to-End 5-Stage Technical Pipeline")

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Card: 5 Pipeline Stages
    add_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.15), split_w - Inches(0.50), split_h - Inches(0.30))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "PIPELINE ARCHITECTURE STAGES"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag.space_after = Pt(4)

    stages = [
        ("Stage 0 • Sensor Photometric Lock:", "Lock Camera2 auto-exposure, gain, and white balance to eliminate artificial sensor drift."),
        ("Stage 1 • Facial Landmark ROI Tracking:", "Track facial mesh landmarks to dynamically isolate perfused forehead skin pixels."),
        ("Stage 2 • Chrominance Subspace (POS):", "Project RGB channels orthogonal to skin-tone vectors to cancel specular reflections (8.9 dB SNR)."),
        ("Stage 3 • Dual-Stream DSP Filtering:", "Resample to 125 Hz via PCHIP, apply Butterworth bandpass and Savitzky-Golay polynomial smoothing."),
        ("Stage 4 • Deep Sequence Regression:", "Feed conditioned pulse waves into 1D-ResNet + BiGRU + Attention for instantaneous SBP/DBP inference.")
    ]

    for label, desc in stages:
        pb = tf_l.add_paragraph()
        pb.space_after = Pt(7)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TITLE_NAVY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Diagram
    right_left = Inches(0.8) + split_w + split_gap
    add_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_BG_WHITE, border_color=COLOR_CARD_BORDER)

    img_path = os.path.join(ASSETS_DIR, "fig_pipeline_overview.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 2: End-to-End Smartphone Ingestion & Deep Sequence Inference Workflow"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9.5)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_9_work_details_demo(prs):
    """Slide 9: Proposed Project Work Details & Live Demo Switch."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 10: Proposed Project Work Details", "Neural Architecture & Live Demonstration")

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Card: Model Architecture Specifications
    add_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.15), split_w - Inches(0.50), split_h - Inches(0.30))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "NEURAL ARCHITECTURE (MODEL-06-SEPHEAD)"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag.space_after = Pt(4)

    specs = [
        ("Input Tensor Representation:", "1 × 1250 standardized optical pulse samples (10-second window @ 125 Hz) + demographic metadata."),
        ("Multi-Scale 1D-ResNet Branches:", "Branch 1 (Kernel=5, Stride=2) extracts sharp systolic peaks; Branch 2 (Kernel=11, Dilated) extracts global waveform rhythms."),
        ("Temporal Sequence Modeling:", "2-layer Bidirectional GRU (hidden=64) captures cardiac phase periodicity across successive heartbeats."),
        ("Multi-Head Self-Attention:", "4-head temporal attention mechanism weights high-SNR cardiac cycles over motion-affected cycles."),
        ("Decoupled Regression Heads:", "Separate dense output heads predicting SBP (stroke volume) and DBP (peripheral resistance) independently.")
    ]

    for label, desc in specs:
        pb = tf_l.add_paragraph()
        pb.space_after = Pt(6)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TITLE_NAVY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Top Card: Architecture Diagram
    right_left = Inches(0.8) + split_w + split_gap
    diagram_h = Inches(3.20)
    add_card(slide, right_left, top_pos, split_w, diagram_h, fill_color=COLOR_BG_WHITE, border_color=COLOR_CARD_BORDER)

    img_path = os.path.join(ASSETS_DIR, "fig_model06_architecture.png")
    add_image_fit(slide, img_path, right_left + Inches(0.15), top_pos + Inches(0.10), split_w - Inches(0.30), diagram_h - Inches(0.40))

    # Right Bottom Card: DEDICATED LIVE DEMO SWITCH CARD
    demo_top = top_pos + diagram_h + Inches(0.15)
    demo_h = split_h - diagram_h - Inches(0.15)
    demo_card = add_card(slide, right_left, demo_top, split_w, demo_h, fill_color=RGBColor(238, 242, 255), border_color=COLOR_BLUE_ACCENT, border_width=Pt(1.5))

    tb_demo = slide.shapes.add_textbox(right_left + Inches(0.20), demo_top + Inches(0.12), split_w - Inches(0.40), demo_h - Inches(0.24))
    tf_d = tb_demo.text_frame
    tf_d.word_wrap = True

    p_d1 = tf_d.paragraphs[0]
    p_d1.text = "⚡ LIVE DEMONSTRATION TOUCHPOINT"
    p_d1.font.name = FONT_HEADING
    p_d1.font.size = Pt(10)
    p_d1.font.bold = True
    p_d1.font.color.rgb = COLOR_BLUE_ACCENT
    p_d1.space_after = Pt(2)

    p_d2 = tf_d.add_paragraph()
    p_d2.text = "📱 [Switching to Smartphone for Live Prototype Demo]"
    p_d2.font.name = FONT_HEADING
    p_d2.font.size = Pt(12)
    p_d2.font.bold = True
    p_d2.font.color.rgb = COLOR_TITLE_NAVY
    p_d2.space_after = Pt(3)

    p_d3 = tf_d.add_paragraph()
    p_d3.text = "Demonstrating real-time Android Camera2 video ingestion, forehead ROI tracking, Savitzky-Golay signal smoothing, and live blood pressure inference on device."
    p_d3.font.name = FONT_BODY
    p_d3.font.size = Pt(9.5)
    p_d3.font.color.rgb = COLOR_TEXT_PRIMARY

    return slide

def build_slide_10_results(prs):
    """Slide 10: Expected Outcomes & Results of the Proposed Project Work."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 11: Expected Outcomes & Results of the Proposed Project Work", "Experimental Benchmarks & Validation Metrics")

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Card: Quantitative Outcomes & Progression Table
    add_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.15), split_w - Inches(0.50), split_h - Inches(0.30))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "MODEL PROGRESSION & EXPLORATORY METRICS"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag.space_after = Pt(4)

    metrics = [
        ("Exploratory Subject MAE:", "10.12 mmHg (SBP) / 5.91 mmHg (DBP) on synchronized evaluation partitions."),
        ("Model Progression Gain:", "Reduced SBP error by 6.70 mmHg compared to naive linear baselines (MODEL-01: 16.82 → MODEL-06: 10.12 mmHg)."),
        ("Signal Extraction SNR:", "POS chrominance projection achieves 8.9 dB SNR; TS-CAN spatial attention achieves 10.4 dB SNR."),
        ("Edge Mobile Latency:", "~120 ms offline batch inference on commodity Android CPU with zero dropped frames."),
        ("Single-Point Calibration:", "Anchoring initial reference reading resolves arterial stiffness variance and prevents population mean collapse.")
    ]

    for label, desc in metrics:
        pb = tf_l.add_paragraph()
        pb.space_after = Pt(7)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TITLE_NAVY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Benchmark Chart
    right_left = Inches(0.8) + split_w + split_gap
    add_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_BG_WHITE, border_color=COLOR_CARD_BORDER)

    img_path = os.path.join(ASSETS_DIR, "fig_extractor_benchmark_chart.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 3: rPPG Extractor SNR & Model Error (MAE) Benchmark Comparison"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9.5)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_11_conclusion(prs):
    """Slide 11: Conclusion remarks & Future Scope of work."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_slide_bg(slide)
    add_header(slide, "Slide 12: Conclusion remarks & Future Scope of work", "Summary & Capstone Roadmap")

    split_w = Inches(5.76)
    split_h = Inches(4.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Card: Conclusions
    add_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.18), split_w - Inches(0.50), split_h - Inches(0.36))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag1 = tf_l.paragraphs[0]
    p_tag1.text = "CONCLUDING REMARKS"
    p_tag1.font.name = FONT_HEADING
    p_tag1.font.size = Pt(9.5)
    p_tag1.font.bold = True
    p_tag1.font.color.rgb = COLOR_BLUE_ACCENT
    p_tag1.space_after = Pt(4)

    conclusions = [
        ("Comprehensive VT Foundation:", "The 6-week Vocational Training at IIIT-NR provided a strong theoretical and practical grounding across 45 AI with Python topics."),
        ("Applied Interdisciplinary Bridge:", "Applying digital signal filtering (Savitzky-Golay) and deep sequence models (CNN-BiGRU-Attention) to optical pulse waveforms proved highly effective."),
        ("Feasibility Confirmed:", "Exploratory results confirm that standard smartphone cameras can capture meaningful cardiovascular vitals without dedicated hardware."),
        ("Privacy-Preserving Paradigm:", "On-device edge inference ensures zero sensitive biometric video data leaves the user's mobile device.")
    ]

    for label, desc in conclusions:
        pb = tf_l.add_paragraph()
        pb.space_after = Pt(6)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TITLE_NAVY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Future Scope
    right_left = Inches(0.8) + split_w + split_gap
    add_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_CARD_FILL, border_color=COLOR_CARD_BORDER)

    tb_right = slide.shapes.add_textbox(right_left + Inches(0.25), top_pos + Inches(0.18), split_w - Inches(0.50), split_h - Inches(0.36))
    tf_r = tb_right.text_frame
    tf_r.word_wrap = True

    p_tag2 = tf_r.paragraphs[0]
    p_tag2.text = "FUTURE SCOPE & CAPSTONE ROADMAP"
    p_tag2.font.name = FONT_HEADING
    p_tag2.font.size = Pt(9.5)
    p_tag2.font.bold = True
    p_tag2.font.color.rgb = COLOR_AMBER_ACCENT
    p_tag2.space_after = Pt(4)

    future = [
        ("Diverse Demographic Trials:", "Conduct extensive evaluations across varied skin tones (Fitzpatrick types I–VI) and ambient lighting conditions."),
        ("Mobile NPU Acceleration:", "Integrate Android NNAPI and INT8 quantization delegates for sub-50ms real-time continuous inference."),
        ("Multi-Modal Optical Fusion:", "Combine front-camera facial rPPG with rear-camera fingertip contact PPG for optical Pulse Transit Time (PTT) estimation."),
        ("Clinical Kiosk Integration:", "Deploy edge inference on smart mirrors and digital healthcare triage kiosks for contactless community screening.")
    ]

    for label, desc in future:
        pb = tf_r.add_paragraph()
        pb.space_after = Pt(6)
        
        r1 = pb.add_run()
        r1.text = f"• {label} "
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(9.5)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TITLE_NAVY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Acknowledgement & Q&A Banner
    bottom_top = top_pos + split_h + Inches(0.15)
    bottom_h = Inches(0.85)
    bottom_card = add_card(slide, Inches(0.8), bottom_top, Inches(11.733), bottom_h, fill_color=COLOR_CARD_HIGHLIGHT, border_color=COLOR_BLUE_ACCENT, border_width=Pt(1))

    tb_bot = slide.shapes.add_textbox(Inches(1.0), bottom_top + Inches(0.10), Inches(11.333), Inches(0.65))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True

    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "Sincere Gratitude to Dr. Anurag Singh (IIIT-NR), Prof. Aparna Pandey (BIT Raipur), Faculty Members & Committee Reviewers"
    p_b1.font.name = FONT_HEADING
    p_b1.font.size = Pt(11)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_TITLE_NAVY
    p_b1.alignment = PP_ALIGN.CENTER
    p_b1.space_after = Pt(2)

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "— Thank You  •  Open for Questions & Feedback —"
    p_b2.font.name = FONT_HEADING
    p_b2.font.size = Pt(10.5)
    p_b2.font.bold = True
    p_b2.font.color.rgb = COLOR_BLUE_ACCENT
    p_b2.alignment = PP_ALIGN.CENTER

    return slide

# =============================================================================
# 4. MAIN DECK BUILDER & EXPORTER
# =============================================================================

def build_all():
    print("============================================================")
    print("BUILDING REDESIGNED MODERN ACADEMIC TECH PPT DECK")
    print("============================================================")
    
    prs = create_presentation()

    print("Building Slide 1: Title Slide & Institutional Acknowledgement...")
    build_slide_1_title(prs)

    print("Building Slide 2: Introduction about the training undergone...")
    build_slide_2_intro(prs)

    print("Building Slide 3: Training Objectives...")
    build_slide_3_objectives(prs)

    print("Building Slide 4: Training Modules / Topics Covered...")
    build_slide_4_curriculum(prs)

    print("Building Slide 5: Key Learnings...")
    build_slide_5_learnings(prs)

    print("Building Slide 6: Proposed Project Title & its Introduction...")
    build_slide_6_proposal(prs)

    print("Building Slide 7: Objectives of the Proposed Project...")
    build_slide_7_objectives_project(prs)

    print("Building Slide 8: Methodology / Approach of the Proposed Project...")
    build_slide_8_methodology(prs)

    print("Building Slide 9: Proposed Project Work Details & Live Demo Switch...")
    build_slide_9_work_details_demo(prs)

    print("Building Slide 10: Expected Outcomes & Results...")
    build_slide_10_results(prs)

    print("Building Slide 11: Conclusion remarks & Future Scope of work...")
    build_slide_11_conclusion(prs)

    # Save outputs
    prs.save(FULL_OUTPUT)
    print(f"Saved primary deck to: {FULL_OUTPUT}")

    prs.save(REDESIGN_OUT)
    print(f"Saved redesign deck to: {REDESIGN_OUT}")

    prs.save(DOWNLOADS_OUT)
    print(f"Saved update to Downloads: {DOWNLOADS_OUT}")

    print("============================================================")
    print("ALL SLIDES SUCCESSFULLY COMPILED!")
    print("============================================================")

if __name__ == "__main__":
    build_all()
