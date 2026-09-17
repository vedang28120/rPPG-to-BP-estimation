r"""
generate_ultimate_deck.py

World-Class Studio-Grade Presentation Architecture.
Features:
  - Deep Midnight Obsidian Canvas (#080C14 to #0E1726)
  - Glassmorphic Translucent Dark Cards (#111827 / #1E293B) with glowing neon borders (#38BDF8 / #F59E0B / #10B981 / #818CF8)
  - Smooth native Slide Transitions (PowerPoint XML <p:transition><p:fade/></p:transition>)
  - Tightly-fitted modular components eliminating empty box syndrome
  - Official BIT Raipur Logo framed with glassmorphism
  - 45 Topics from Topics Covered.txt categorized into 5 glowing domain cards
  - Dedicated High-Voltage "⚡ LIVE MOBILE DEMO TOUCHPOINT" on Slide 9/10
  - Aspect-ratio preserved high-res figures
  - Humble, grateful, and academically rigorous tone

Outputs:
  - presentation/VT_2026_rPPG_to_BP_Estimation.pptx (Primary Defense Deck)
  - presentation/VT_2026_Ultimate_Studio_Deck.pptx
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
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# =============================================================================
# 1. COLOR SYSTEM & DESIGN TOKENS (DEEP CYBER-STUDIO DARK THEME)
# =============================================================================
COLOR_BG_DARK        = RGBColor(8, 12, 20)      # #080C14 Deep Midnight Obsidian
COLOR_CARD_BG        = RGBColor(17, 24, 39)     # #111827 Dark Slate 900
COLOR_CARD_ALT       = RGBColor(30, 41, 59)     # #1E293B Slate 800
COLOR_CARD_GLOW      = RGBColor(24, 36, 60)     # #18243C Elevated Glass

COLOR_BORDER_MUTED   = RGBColor(51, 65, 85)     # #334155 Slate 700 Border
COLOR_BORDER_CYAN    = RGBColor(56, 189, 248)   # #38BDF8 Neon Cyan Glow
COLOR_BORDER_AMBER   = RGBColor(245, 158, 11)   # #F59E0B Solar Amber Glow
COLOR_BORDER_EMERALD = RGBColor(16, 185, 129)   # #10B981 Emerald Mint Glow
COLOR_BORDER_PURPLE  = RGBColor(168, 85, 247)   # #A855F7 Violet Neon Glow
COLOR_BORDER_ROSE    = RGBColor(244, 63, 94)    # #F43F5E Rose Accent Glow

COLOR_TEXT_HERO      = RGBColor(255, 255, 255) # #FFFFFF Crisp Pure White
COLOR_TEXT_PRIMARY   = RGBColor(241, 245, 249) # #F1F5F9 Slate 100
COLOR_TEXT_MUTED     = RGBColor(148, 163, 184) # #94A3B8 Slate 400
COLOR_TEXT_DIM       = RGBColor(100, 116, 139) # #64748B Slate 500

COLOR_NEON_CYAN      = RGBColor(6, 182, 212)   # #06B6D4
COLOR_NEON_BLUE      = RGBColor(59, 130, 246)  # #3B82F6
COLOR_NEON_AMBER     = RGBColor(245, 158, 11)  # #F59E0B
COLOR_NEON_EMERALD   = RGBColor(16, 185, 129)  # #10B981
COLOR_NEON_PURPLE    = RGBColor(139, 92, 246)  # #8B5CF6

FONT_HEADING = "Arial"
FONT_BODY    = "Calibri"

SLIDE_WIDTH_INCHES  = 13.333
SLIDE_HEIGHT_INCHES = 7.500

WORKSPACE_DIR = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation"
ASSETS_DIR    = os.path.join(WORKSPACE_DIR, "presentation", "assets")
FULL_OUTPUT   = os.path.join(WORKSPACE_DIR, "presentation", "VT_2026_rPPG_to_BP_Estimation.pptx")
STUDIO_OUTPUT = os.path.join(WORKSPACE_DIR, "presentation", "VT_2026_Ultimate_Studio_Deck.pptx")
DOWNLOADS_OUT = r"C:\Users\simpl\Downloads\Sample PPT _VT 2026.pptx"

# =============================================================================
# 2. CORE HELPER FUNCTIONS & NATIVE PPTX ENHANCEMENTS
# =============================================================================

def create_presentation():
    """Initializes a 16:9 widescreen presentation."""
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
    prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)
    return prs

def apply_studio_bg(slide):
    """Fills slide background with deep obsidian and injects smooth fade transition."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG_DARK

    # Inject native PowerPoint smooth fade transition
    try:
        trans_xml = parse_xml(f'<p:transition {nsdecls("p")} spd="med"><p:fade/></p:transition>')
        slide._element.append(trans_xml)
    except Exception as e:
        pass

def add_header_banner(slide, title, category=None, category_color=COLOR_NEON_CYAN):
    """
    Studio Header Banner with Category Tag, Glow Underline, and crisp navigation pill.
    """
    # Category Pill
    if category:
        cat_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.40), Inches(4.5), Inches(0.32))
        cat_box.fill.solid()
        cat_box.fill.fore_color.rgb = COLOR_CARD_BG
        cat_box.line.color.rgb = category_color
        cat_box.line.width = Pt(1)

        ctf = cat_box.text_frame
        ctf.word_wrap = False
        cp = ctf.paragraphs[0]
        cp.text = f"✦  {category.upper()}"
        cp.font.name = FONT_HEADING
        cp.font.size = Pt(8.5)
        cp.font.bold = True
        cp.font.color.rgb = category_color
        cp.alignment = PP_ALIGN.CENTER

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.733), Inches(0.55))
    tf = title_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_HERO

    # Sleek Gradient Accent Line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.36), Inches(11.733), Pt(1.5))
    line.fill.solid()
    line.fill.fore_color.rgb = category_color
    line.line.color.rgb = category_color
    line.line.width = Pt(0)

def add_glass_card(slide, left, top, width, height, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_MUTED, border_width=Pt(1)):
    """Creates a sleek glassmorphic container with custom border glow."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = border_width
    return card

def add_image_fit(slide, img_path, box_left, box_top, box_width, box_height):
    """Aspect-ratio preserving image placement."""
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
# 3. ULTIMATE SLIDE BUILDERS (STUDIO EDITION)
# =============================================================================

def build_slide_1_hero_title(prs):
    """Slide 1: Hero Launchpad Title Slide with BIT Logo & Studio Glass Cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)

    # Logo Glass Card at Top-Left
    logo_path = os.path.join(ASSETS_DIR, "image1.jpeg")
    logo_card = add_glass_card(slide, Inches(0.8), Inches(0.45), Inches(1.35), Inches(1.35), fill_color=COLOR_CARD_ALT, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))
    if os.path.exists(logo_path):
        add_image_fit(slide, logo_path, Inches(0.85), Inches(0.50), Inches(1.25), Inches(1.25))

    # Top Tagline Pill
    tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.35), Inches(0.48), Inches(10.18), Inches(0.35))
    tag_box.fill.solid()
    tag_box.fill.fore_color.rgb = COLOR_CARD_BG
    tag_box.line.color.rgb = COLOR_BORDER_CYAN
    tag_box.line.width = Pt(1)

    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = False
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "✦  VOCATIONAL TRAINING REPORT & PROPOSED CAPSTONE PROJECT DEFENSE  ✦"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_NEON_CYAN
    p_tag.alignment = PP_ALIGN.CENTER

    # Hero Title Textbox
    title_box = slide.shapes.add_textbox(Inches(2.35), Inches(0.90), Inches(10.18), Inches(1.25))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = "Mobile Remote Photoplethysmography to\nCuffless Blood Pressure Estimation"
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_HERO
    p_title.alignment = PP_ALIGN.LEFT

    # Subtitle: Training Details
    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.25), Inches(11.733), Inches(0.45))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Vocational Training on 'AI with Python' (IIIT Naya Raipur • 01/07/2026 to 10/08/2026)"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(13)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_NEON_AMBER
    p_sub.alignment = PP_ALIGN.LEFT

    # Center Metadata Container (Presenters, Mentors, College)
    meta_card = add_glass_card(slide, Inches(0.8), Inches(2.78), Inches(11.733), Inches(2.15), fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_MUTED)

    # 3-Column Internal Layout for Presenters, Mentors, Institution
    col_w = Inches(3.70)
    col_gap = Inches(0.18)

    # Column 1: Presenters
    tb_p = slide.shapes.add_textbox(Inches(0.95), Inches(2.90), col_w, Inches(1.90))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    
    p_ph = tf_p.paragraphs[0]
    p_ph.text = "STUDENT RESEARCHERS (4th Sem)"
    p_ph.font.name = FONT_HEADING
    p_ph.font.size = Pt(9.5)
    p_ph.font.bold = True
    p_ph.font.color.rgb = COLOR_NEON_CYAN
    p_ph.space_after = Pt(4)

    for name in ["1. Vedang Bhatt", "2. Anubhav Shrivastav", "3. Aadarsh"]:
        p_n = tf_p.add_paragraph()
        p_n.text = f"• {name}"
        p_n.font.name = FONT_HEADING
        p_n.font.size = Pt(11)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_TEXT_PRIMARY
        p_n.space_after = Pt(2)

    # Column 2: Mentors
    tb_m = slide.shapes.add_textbox(Inches(0.95) + col_w + col_gap, Inches(2.90), col_w, Inches(1.90))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    p_mh = tf_m.paragraphs[0]
    p_mh.text = "INSTITUTIONAL MENTORS"
    p_mh.font.name = FONT_HEADING
    p_mh.font.size = Pt(9.5)
    p_mh.font.bold = True
    p_mh.font.color.rgb = COLOR_NEON_AMBER
    p_mh.space_after = Pt(4)

    mentors_list = [
        ("VT Mentor:", "Dr. Anurag Singh (IIIT-NR)"),
        ("College Mentor:", "Prof. Aparna Pandey (BIT Raipur)")
    ]
    for role, mname in mentors_list:
        p_m1 = tf_m.add_paragraph()
        p_m1.text = role
        p_m1.font.name = FONT_BODY
        p_m1.font.size = Pt(9)
        p_m1.font.color.rgb = COLOR_TEXT_MUTED
        
        p_m2 = tf_m.add_paragraph()
        p_m2.text = mname
        p_m2.font.name = FONT_HEADING
        p_m2.font.size = Pt(11)
        p_m2.font.bold = True
        p_m2.font.color.rgb = COLOR_TEXT_PRIMARY
        p_m2.space_after = Pt(3)

    # Column 3: Department & Affiliation
    tb_d = slide.shapes.add_textbox(Inches(0.95) + (col_w + col_gap) * 2, Inches(2.90), col_w, Inches(1.90))
    tf_d = tb_d.text_frame
    tf_d.word_wrap = True

    p_dh = tf_d.paragraphs[0]
    p_dh.text = "ACADEMIC DEPARTMENT"
    p_dh.font.name = FONT_HEADING
    p_dh.font.size = Pt(9.5)
    p_dh.font.bold = True
    p_dh.font.color.rgb = COLOR_NEON_EMERALD
    p_dh.space_after = Pt(4)

    p_dt = tf_d.add_paragraph()
    p_dt.text = "Department of Computer Science & Engineering"
    p_dt.font.name = FONT_HEADING
    p_dt.font.size = Pt(11)
    p_dt.font.bold = True
    p_dt.font.color.rgb = COLOR_TEXT_PRIMARY
    p_dt.space_after = Pt(2)

    p_di = tf_d.add_paragraph()
    p_di.text = "Bhilai Institute of Technology, Raipur\nAffiliated to CSVTU, Bhilai"
    p_di.font.name = FONT_BODY
    p_di.font.size = Pt(9.5)
    p_di.font.color.rgb = COLOR_TEXT_MUTED

    # 3 High-Voltage Bottom Showcase Pills
    pill_w = Inches(3.77)
    pill_gap = Inches(0.20)
    pill_top = Inches(5.12)
    pill_h = Inches(1.85)

    pills_data = [
        ("AI WITH PYTHON", "IIIT-NR Training Immersion", "6-week intensive exposure across 45 structured topics from data wrangling to agentic AI tools.", COLOR_BORDER_CYAN, COLOR_NEON_CYAN),
        ("APPLIED DSP & DL", "Signal Filtering to Deep Regressors", "Savitzky-Golay polynomial smoothing synergized with 1D-CNN + BiGRU + Self-Attention in TensorFlow.", COLOR_BORDER_AMBER, COLOR_NEON_AMBER),
        ("CAPSTONE PROPOSAL", "Contactless Cardiovascular Vitals", "Smartphone front-camera rPPG pipeline for non-invasive, privacy-preserving continuous BP tracking.", COLOR_BORDER_EMERALD, COLOR_NEON_EMERALD)
    ]

    for i, (tag, title, desc, b_color, t_color) in enumerate(pills_data):
        c_left = Inches(0.8) + i * (pill_w + pill_gap)
        add_glass_card(slide, c_left, pill_top, pill_w, pill_h, fill_color=COLOR_CARD_BG, border_color=b_color, border_width=Pt(1))

        # Top Glow Bar
        glow_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, pill_top, pill_w, Inches(0.06))
        glow_bar.fill.solid()
        glow_bar.fill.fore_color.rgb = t_color
        glow_bar.line.color.rgb = t_color
        glow_bar.line.width = Pt(0)

        tb = slide.shapes.add_textbox(c_left + Inches(0.18), pill_top + Inches(0.12), pill_w - Inches(0.36), pill_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"✦ {tag}"
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(8.5)
        p1.font.bold = True
        p1.font.color.rgb = t_color
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_TEXT_HERO
        p2.space_after = Pt(3)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_2_intro_pillars(prs):
    """Slide 2: Introduction about the training undergone (3 High-Impact Pillars)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 2: Introduction about the training undergone", "Vocational Training Overview @ IIIT-NR", COLOR_NEON_CYAN)

    card_w = Inches(3.77)
    card_gap = Inches(0.20)
    card_top = Inches(1.65)
    card_h = Inches(5.35)

    pillars = [
        {
            "num": "01",
            "tag": "ACADEMIC IMMERSION",
            "title": "Exposure at IIIT-NR",
            "color": COLOR_NEON_CYAN,
            "b_color": COLOR_BORDER_CYAN,
            "bullets": [
                ("Program:", "6-Week Intensive Vocational Training in 'AI with Python'."),
                ("Timeline:", "01/07/2026 to 10/08/2026 (Summer Break after 4th Sem)."),
                ("Objective:", "Bridging classroom computer science theory to professional AI & data science workflows."),
                ("Environment:", "Advanced laboratory environment with expert mentorship under Dr. Anurag Singh.")
            ]
        },
        {
            "num": "02",
            "tag": "PROGRESSIVE CURRICULUM",
            "title": "Comprehensive AI Foundations",
            "color": COLOR_NEON_AMBER,
            "b_color": COLOR_BORDER_AMBER,
            "bullets": [
                ("Data Foundations:", "NumPy vectorization, Pandas wrangling, Matplotlib visualization."),
                ("Classical ML Rigor:", "Supervised/Unsupervised models, bias-variance tradeoffs, K-Fold cross-validation."),
                ("Deep Learning:", "TensorFlow graph execution, activations (Sigmoid, ReLU, SoftMax), CNNs, RNNs & LSTMs."),
                ("Signal Filtering:", "Digital polynomial smoothing using the Savitzky-Golay filter.")
            ]
        },
        {
            "num": "03",
            "tag": "APPLIED CAPSTONE",
            "title": "Modern AI & Project Bridge",
            "color": COLOR_NEON_EMERALD,
            "b_color": COLOR_BORDER_EMERALD,
            "bullets": [
                ("Modern AI Tools:", "Introductory exposure to NLP, Word2Vec, GloVe, Transformer Encoders, RAG, LangChain & MCP."),
                ("Applied Inspiration:", "Formulated an interdisciplinary capstone bridging digital signal processing to contactless vital sensing."),
                ("Privacy Focus:", "100% on-device edge execution eliminating cloud biometric transfer."),
                ("Ethical Humility:", "Honest appraisal of exploratory prototypes and clinical validation boundaries.")
            ]
        }
    ]

    for i, p in enumerate(pillars):
        c_left = Inches(0.8) + i * (card_w + card_gap)
        add_glass_card(slide, c_left, card_top, card_w, card_h, fill_color=COLOR_CARD_BG, border_color=p["b_color"], border_width=Pt(1))

        # Glowing Number Pill
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Inches(0.18), card_top + Inches(0.18), Inches(0.55), Inches(0.55))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CARD_ALT
        badge.line.color.rgb = p["color"]
        badge.line.width = Pt(1)
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = p["num"]
        bp.font.name = FONT_HEADING
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = p["color"]
        bp.alignment = PP_ALIGN.CENTER

        # Tag
        tb_tag = slide.shapes.add_textbox(c_left + Inches(0.85), card_top + Inches(0.18), card_w - Inches(1.05), Inches(0.55))
        tf_t = tb_tag.text_frame
        tf_t.word_wrap = True
        pt1 = tf_t.paragraphs[0]
        pt1.text = p["tag"]
        pt1.font.name = FONT_HEADING
        pt1.font.size = Pt(8.5)
        pt1.font.bold = True
        pt1.font.color.rgb = p["color"]

        pt2 = tf_t.add_paragraph()
        pt2.text = p["title"]
        pt2.font.name = FONT_HEADING
        pt2.font.size = Pt(11.5)
        pt2.font.bold = True
        pt2.font.color.rgb = COLOR_TEXT_HERO

        # Divider
        div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left + Inches(0.18), card_top + Inches(0.85), card_w - Inches(0.36), Pt(1))
        div.fill.solid()
        div.fill.fore_color.rgb = COLOR_BORDER_MUTED
        div.line.width = Pt(0)

        # Bullets
        tb_b = slide.shapes.add_textbox(c_left + Inches(0.18), card_top + Inches(0.95), card_w - Inches(0.36), card_h - Inches(1.10))
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True

        for idx, (label, desc) in enumerate(p["bullets"]):
            pb = tf_b.paragraphs[0] if idx == 0 else tf_b.add_paragraph()
            pb.space_after = Pt(8)

            r1 = pb.add_run()
            r1.text = f"• {label} "
            r1.font.name = FONT_HEADING
            r1.font.size = Pt(9.5)
            r1.font.bold = True
            r1.font.color.rgb = COLOR_TEXT_PRIMARY

            r2 = pb.add_run()
            r2.text = desc
            r2.font.name = FONT_BODY
            r2.font.size = Pt(9)
            r2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_3_objectives_stepper(prs):
    """Slide 3: Training Objectives (Connected 5-Node Stepper)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 3: Training Objectives", "Core Pedagogical Goals @ IIIT-NR", COLOR_NEON_CYAN)

    card_w = Inches(11.733)
    card_h = Inches(0.92)
    card_gap = Inches(0.14)
    start_top = Inches(1.65)

    milestones = [
        ("01", "Python & Scientific Data Foundations", "Master vectorized array operations with NumPy, tabular data manipulation with Pandas, and data visualization with Matplotlib.", COLOR_NEON_CYAN, COLOR_BORDER_CYAN),
        ("02", "Machine Learning Paradigms & Validation Rigor", "Understand supervised/unsupervised algorithms, bias-variance tradeoffs, L1/L2 regularization, and robust K-Fold cross-validation.", COLOR_NEON_BLUE, COLOR_BORDER_MUTED),
        ("03", "Deep Learning & Layer Mechanics in TensorFlow", "Build computational graphs in TensorFlow—mastering activations (Sigmoid, ReLU, SoftMax), backpropagation, CNNs, and sequence models (RNN, LSTM, Self-Attention).", COLOR_NEON_PURPLE, COLOR_BORDER_PURPLE),
        ("04", "Digital Signal Filtering & Mathematical Operations", "Implement Savitzky-Golay digital polynomial smoothing for noise reduction without peak distortion; explore vector Cosine Similarity.", COLOR_NEON_AMBER, COLOR_BORDER_AMBER),
        ("05", "NLP, Transformers & Emerging Agentic AI", "Gain exposure to Word2Vec, GloVe, Contextual Embeddings, Transformer Encoders, RAG architecture, LangChain orchestration, and Agentic AI tools / MCP.", COLOR_NEON_EMERALD, COLOR_BORDER_EMERALD)
    ]

    for i, (num, title, desc, accent, b_color) in enumerate(milestones):
        top_pos = start_top + i * (card_h + card_gap)
        add_glass_card(slide, Inches(0.8), top_pos, card_w, card_h, fill_color=COLOR_CARD_BG, border_color=b_color, border_width=Pt(1))

        # Node Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), top_pos + Inches(0.15), Inches(0.62), Inches(0.62))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CARD_ALT
        badge.line.color.rgb = accent
        badge.line.width = Pt(1.5)
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = num
        bp.font.name = FONT_HEADING
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = accent
        bp.alignment = PP_ALIGN.CENTER

        # Content
        tb = slide.shapes.add_textbox(Inches(1.75), top_pos + Inches(0.10), Inches(10.60), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_HERO
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_4_curriculum_matrix(prs):
    """Slide 4: Training Modules / Topics Covered (5 Distinct Neon Domain Cards)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 4: Training Modules / Topics Covered", "Comprehensive 45-Topic Syllabus @ IIIT-NR", COLOR_NEON_AMBER)

    col_w = Inches(2.22)
    col_gap = Inches(0.15)
    col_top = Inches(1.65)
    col_h = Inches(5.35)

    modules = [
        {
            "mod": "MOD 1",
            "title": "Python & Data",
            "accent": COLOR_NEON_CYAN,
            "border": COLOR_BORDER_CYAN,
            "topics": [
                "Python basics & syntax",
                "NumPy array vectorization",
                "Pandas data wrangling",
                "Matplotlib visualizations",
                "Data preprocessing flow",
                "Feature scaling & norms"
            ]
        },
        {
            "mod": "MOD 2",
            "title": "ML Rigor",
            "accent": COLOR_NEON_BLUE,
            "border": COLOR_BORDER_MUTED,
            "topics": [
                "Supervised & Unsupervised",
                "Semi-Supervised & RL",
                "Linear & Polynomial Reg.",
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
            "accent": COLOR_NEON_PURPLE,
            "border": COLOR_BORDER_PURPLE,
            "topics": [
                "TensorFlow ecosystem",
                "Computational graphs",
                "Backpropagation math",
                "Activations: Sigmoid, ReLU, SoftMax",
                "Layers: Conv, Pool, Dense",
                "CNN architectures",
                "DNN, RNN & LSTM models",
                "Self-Attention primitives"
            ]
        },
        {
            "mod": "MOD 4",
            "title": "Signal & NLP",
            "accent": COLOR_NEON_AMBER,
            "border": COLOR_BORDER_AMBER,
            "topics": [
                "Savitzky-Golay filter",
                "NLP foundations & NLTK",
                "Word-to-vec embeddings",
                "GloVe representations",
                "Sequence encoders",
                "Contextual embeddings",
                "Vector Cosine Similarity"
            ]
        },
        {
            "mod": "MOD 5",
            "title": "GenAI & Agents",
            "accent": COLOR_NEON_EMERALD,
            "border": COLOR_BORDER_EMERALD,
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
        add_glass_card(slide, c_left, col_top, col_w, col_h, fill_color=COLOR_CARD_BG, border_color=m["border"], border_width=Pt(1))

        # Header Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Inches(0.12), col_top + Inches(0.12), col_w - Inches(0.24), Inches(0.48))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CARD_ALT
        badge.line.color.rgb = m["accent"]
        badge.line.width = Pt(1)

        btf = badge.text_frame
        bp1 = btf.paragraphs[0]
        bp1.text = m["mod"]
        bp1.font.name = FONT_HEADING
        bp1.font.size = Pt(8)
        bp1.font.bold = True
        bp1.font.color.rgb = m["accent"]
        bp1.alignment = PP_ALIGN.CENTER

        bp2 = btf.add_paragraph()
        bp2.text = m["title"]
        bp2.font.name = FONT_HEADING
        bp2.font.size = Pt(9.5)
        bp2.font.bold = True
        bp2.font.color.rgb = COLOR_TEXT_HERO
        bp2.alignment = PP_ALIGN.CENTER

        # Topics List
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

def build_slide_5_key_learnings(prs):
    """Slide 5: Key Learnings (2x2 Matrix with Glowing Badges)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 5: Key Learnings", "Practical Insights Gained Under Mentorship", COLOR_NEON_AMBER)

    card_w = Inches(5.76)
    card_h = Inches(2.55)
    card_gap = Inches(0.20)
    top_r1 = Inches(1.65)
    top_r2 = top_r1 + card_h + card_gap

    learnings = [
        (
            "DATA PREPROCESSING & RIGOR",
            "1. Real-World Signals Require Rigorous Preprocessing",
            "Real-world data—whether tabular, audio, or physiological—carries severe baseline wander and sensor noise. Standardizing feature distributions, robust encoding, and using K-fold cross-validation are indispensable before training any deep neural network.",
            COLOR_NEON_CYAN,
            COLOR_BORDER_CYAN,
            Inches(0.8),
            top_r1
        ),
        (
            "SIGNAL PROCESSING INSIGHT",
            "2. Digital Smoothing Preserves Critical Peak Extrema",
            "Learning digital signal smoothing techniques like the Savitzky-Golay filter demonstrated how local polynomial regression effectively removes high-frequency noise while preserving vital systolic/diastolic peak extrema without distorting signal morphology.",
            COLOR_NEON_AMBER,
            COLOR_BORDER_AMBER,
            Inches(0.8) + card_w + card_gap,
            top_r1
        ),
        (
            "NEURAL ARCHITECTURE DESIGN",
            "3. Synergy of Convolutional & Recurrent / Attention Layers",
            "Understanding CNNs and LSTMs in TensorFlow revealed that combining 1D convolutions (for localized morphological feature extraction) with recurrent and self-attention layers (for temporal cardiac periodicity) provides superior time-series representation.",
            COLOR_NEON_PURPLE,
            COLOR_BORDER_PURPLE,
            Inches(0.8),
            top_r2
        ),
        (
            "CAPSTONE INSPIRATION",
            "4. Applied Exploration: Optical Blood Pressure Estimation",
            "Guided by our coursework in Python, signal processing, and deep neural models, we formulated our undergraduate capstone project: extracting transcutaneous optical pulse signals from smartphone cameras to explore cuffless blood pressure estimation.",
            COLOR_NEON_EMERALD,
            COLOR_BORDER_EMERALD,
            Inches(0.8) + card_w + card_gap,
            top_r2
        )
    ]

    for tag, title, desc, accent, border, left, top in learnings:
        add_glass_card(slide, left, top, card_w, card_h, fill_color=COLOR_CARD_BG, border_color=border, border_width=Pt(1))

        # Corner Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.20), top + Inches(0.16), Inches(2.6), Inches(0.30))
        pill.fill.solid()
        pill.fill.fore_color.rgb = COLOR_CARD_ALT
        pill.line.color.rgb = accent
        pill.line.width = Pt(1)

        ptf = pill.text_frame
        pp = ptf.paragraphs[0]
        pp.text = f"✦ {tag}"
        pp.font.name = FONT_HEADING
        pp.font.size = Pt(8)
        pp.font.bold = True
        pp.font.color.rgb = accent
        pp.alignment = PP_ALIGN.CENTER

        tb = slide.shapes.add_textbox(left + Inches(0.20), top + Inches(0.52), card_w - Inches(0.40), card_h - Inches(0.60))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_HERO
        p1.space_after = Pt(5)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_6_proposed_project(prs):
    """Slide 6: Proposed Project Title & its Introduction (Split Studio Card)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 6: Proposed Project Title & its Introduction", "Proposed Capstone Project Definition", COLOR_NEON_CYAN)

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Glass Card: Motivation
    add_glass_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.18), split_w - Inches(0.50), split_h - Inches(0.36))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "✦ PROPOSED CAPSTONE PROJECT TITLE"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_NEON_CYAN
    p_tag.space_after = Pt(2)

    p_t = tf_l.add_paragraph()
    p_t.text = "Mobile Remote Photoplethysmography (rPPG) to Cuffless Blood Pressure Estimation"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TEXT_HERO
    p_t.space_after = Pt(10)

    bullets = [
        ("Global Clinical Challenge:", "Hypertension impacts >1.28B adults globally as a primary asymptomatic cardiovascular risk factor."),
        ("Limitations of Arm Cuffs:", "Traditional inflatable cuffs are intermittent, uncomfortable, and disrupt sleep during 24-hour monitoring."),
        ("White-Coat Effect:", "In-clinic cuff pressure induces acute stress responses, frequently causing false-positive hypertension readings."),
        ("Contactless Optical Concept:", "Smartphone RGB cameras detect subtle facial color variations caused by blood volume pulses, estimating continuous blood pressure non-invasively.")
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

    # Right Card: Dark-Framed Diagram
    right_left = Inches(0.8) + split_w + split_gap
    add_glass_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_CARD_ALT, border_color=COLOR_BORDER_MUTED, border_width=Pt(1))

    img_path = os.path.join(ASSETS_DIR, "fig_windkessel_damping.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 1: Transcutaneous Optical Absorption & Hemodynamic Waveform Dynamics"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_7_objectives_project(prs):
    """Slide 7: Objectives of the Proposed Project (5 Spec Pillars)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 7: Objectives of the Proposed Project", "System Specifications & Engineering Deliverables", COLOR_NEON_CYAN)

    card_w = Inches(11.733)
    card_h = Inches(0.92)
    card_gap = Inches(0.14)
    start_top = Inches(1.65)

    deliverables = [
        ("01", "Optical Pulse Extraction via Smartphone Camera", "Capture facial video at 30 FPS using locked camera parameters; isolate forehead microvascular ROIs and extract rPPG pulse waveforms via POS chrominance projection.", COLOR_NEON_CYAN, COLOR_BORDER_CYAN),
        ("02", "Physiological Signal Denoising & Conditioning", "Standardize variable frame rates to a uniform 125 Hz grid via PCHIP interpolation and apply Savitzky-Golay polynomial smoothing + Butterworth bandpass (0.75–2.5 Hz).", COLOR_NEON_BLUE, COLOR_BORDER_MUTED),
        ("03", "Deep Neural Sequence Regression", "Develop a hybrid deep architecture (1D-CNN feature extraction + BiGRU sequence modeling + Self-Attention) in TensorFlow with decoupled linear heads for SBP and DBP.", COLOR_NEON_PURPLE, COLOR_BORDER_PURPLE),
        ("04", "Single-Point Personal Calibration Study", "Investigate single-point baseline calibration to anchor individual vascular tone and arterial stiffness, overcoming physiological 'template collapse'.", COLOR_NEON_AMBER, COLOR_BORDER_AMBER),
        ("05", "Privacy-Preserving On-Device Mobile Execution", "Optimize model inference for lightweight Android execution (using TFLite quantization), ensuring 100% on-device privacy with zero cloud transmission.", COLOR_NEON_EMERALD, COLOR_BORDER_EMERALD)
    ]

    for i, (num, title, desc, accent, b_color) in enumerate(deliverables):
        top_pos = start_top + i * (card_h + card_gap)
        add_glass_card(slide, Inches(0.8), top_pos, card_w, card_h, fill_color=COLOR_CARD_BG, border_color=b_color, border_width=Pt(1))

        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), top_pos + Inches(0.15), Inches(0.62), Inches(0.62))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CARD_ALT
        badge.line.color.rgb = accent
        badge.line.width = Pt(1.5)
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = num
        bp.font.name = FONT_HEADING
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = accent
        bp.alignment = PP_ALIGN.CENTER

        tb = slide.shapes.add_textbox(Inches(1.75), top_pos + Inches(0.10), Inches(10.60), Inches(0.72))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(11.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_HERO
        p1.space_after = Pt(2)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_8_methodology(prs):
    """Slide 8: Methodology / Approach of the Proposed Project (Pipeline Flow)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 9: Methodology / Approach of the Proposed Project", "End-to-End 5-Stage Technical Pipeline", COLOR_NEON_CYAN)

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Glass Card: 5 Pipeline Stages
    add_glass_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.15), split_w - Inches(0.50), split_h - Inches(0.30))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "✦ 5-STAGE TECHNICAL PIPELINE"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_NEON_CYAN
    p_tag.space_after = Pt(4)

    stages = [
        ("Stage 0 • Sensor Photometric Lock:", "Lock Camera2 auto-exposure, gain, and white balance to eliminate artificial sensor drift."),
        ("Stage 1 • Facial Landmark ROI Tracking:", "Track facial landmarks to dynamically isolate perfused forehead skin pixels."),
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
        r1.font.color.rgb = COLOR_TEXT_PRIMARY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Diagram
    right_left = Inches(0.8) + split_w + split_gap
    add_glass_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_CARD_ALT, border_color=COLOR_BORDER_MUTED, border_width=Pt(1))

    img_path = os.path.join(ASSETS_DIR, "fig_pipeline_overview.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 2: End-to-End Smartphone Ingestion & Deep Sequence Inference Workflow"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_9_work_details_demo(prs):
    """Slide 9: Proposed Project Work Details & High-Voltage LIVE DEMO SPOTLIGHT."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 10: Proposed Project Work Details", "Neural Architecture & Live Demonstration", COLOR_NEON_CYAN)

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Glass Card: Model Architecture
    add_glass_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.15), split_w - Inches(0.50), split_h - Inches(0.30))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag = tf_l.paragraphs[0]
    p_tag.text = "✦ MODEL-06-SEPHEAD ARCHITECTURE"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(9)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_NEON_CYAN
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
        r1.font.color.rgb = COLOR_TEXT_PRIMARY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Top Card: Architecture Diagram
    right_left = Inches(0.8) + split_w + split_gap
    diagram_h = Inches(3.20)
    add_glass_card(slide, right_left, top_pos, split_w, diagram_h, fill_color=COLOR_CARD_ALT, border_color=COLOR_BORDER_MUTED, border_width=Pt(1))

    img_path = os.path.join(ASSETS_DIR, "fig_model06_architecture.png")
    add_image_fit(slide, img_path, right_left + Inches(0.15), top_pos + Inches(0.10), split_w - Inches(0.30), diagram_h - Inches(0.40))

    # Right Bottom Card: HIGH-VOLTAGE LIVE DEMO TOUCHPOINT
    demo_top = top_pos + diagram_h + Inches(0.15)
    demo_h = split_h - diagram_h - Inches(0.15)
    demo_card = add_glass_card(slide, right_left, demo_top, split_w, demo_h, fill_color=COLOR_CARD_GLOW, border_color=COLOR_BORDER_CYAN, border_width=Pt(1.5))

    tb_demo = slide.shapes.add_textbox(right_left + Inches(0.20), demo_top + Inches(0.12), split_w - Inches(0.40), demo_h - Inches(0.24))
    tf_d = tb_demo.text_frame
    tf_d.word_wrap = True

    p_d1 = tf_d.paragraphs[0]
    p_d1.text = "⚡ LIVE DEMONSTRATION TOUCHPOINT"
    p_d1.font.name = FONT_HEADING
    p_d1.font.size = Pt(9.5)
    p_d1.font.bold = True
    p_d1.font.color.rgb = COLOR_NEON_CYAN
    p_d1.space_after = Pt(2)

    p_d2 = tf_d.add_paragraph()
    p_d2.text = "📱 [Switching to Smartphone for Live Prototype Demo]"
    p_d2.font.name = FONT_HEADING
    p_d2.font.size = Pt(11.5)
    p_d2.font.bold = True
    p_d2.font.color.rgb = COLOR_TEXT_HERO
    p_d2.space_after = Pt(3)

    p_d3 = tf_d.add_paragraph()
    p_d3.text = "Demonstrating real-time Android Camera2 video ingestion, forehead ROI tracking, Savitzky-Golay signal smoothing, and live blood pressure inference on device."
    p_d3.font.name = FONT_BODY
    p_d3.font.size = Pt(9)
    p_d3.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def build_slide_10_results_dashboard(prs):
    """Slide 10: Expected Outcomes & Results (Floating Neon KPI Dashboard)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 11: Expected Outcomes & Results of the Proposed Project Work", "Experimental Benchmarks & Validation Metrics", COLOR_NEON_EMERALD)

    split_w = Inches(5.76)
    split_h = Inches(5.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Container: 4 Floating KPI Stat Cards
    kpi_w = split_w
    kpi_h = Inches(1.18)
    kpi_gap = Inches(0.12)

    kpi_items = [
        ("10.12 / 5.91 mmHg", "EXPLORATORY SUBJECT MAE", "Subject-level test error (SBP / DBP) on synchronized video evaluation partitions.", COLOR_NEON_EMERALD, COLOR_BORDER_EMERALD),
        ("6.70 mmHg GAIN", "PROGRESSION OVER BASELINE", "Substantial error reduction achieved over naive linear baselines (MODEL-01: 16.82 → MODEL-06: 10.12).", COLOR_NEON_CYAN, COLOR_BORDER_CYAN),
        ("8.9 dB SNR", "POS CHROMINANCE PROJECTION", "Orthogonal skin-plane projection placing specular white reflection directly in the null space.", COLOR_NEON_AMBER, COLOR_BORDER_AMBER),
        ("120 ms LATENCY", "EDGE MOBILE EXECUTION", "Zero-dropped frames with asynchronous offline batching on commodity Android CPU.", COLOR_NEON_PURPLE, COLOR_BORDER_PURPLE)
    ]

    for i, (val, label, desc, accent, border) in enumerate(kpi_items):
        top_kpi = top_pos + i * (kpi_h + kpi_gap)
        add_glass_card(slide, Inches(0.8), top_kpi, kpi_w, kpi_h, fill_color=COLOR_CARD_BG, border_color=border, border_width=Pt(1))

        # Left Number Box
        tb_val = slide.shapes.add_textbox(Inches(0.95), top_kpi + Inches(0.12), Inches(2.2), kpi_h - Inches(0.24))
        tf_v = tb_val.text_frame
        tf_v.word_wrap = True
        pv = tf_v.paragraphs[0]
        pv.text = val
        pv.font.name = FONT_HEADING
        pv.font.size = Pt(13.5)
        pv.font.bold = True
        pv.font.color.rgb = accent

        # Right Text Box
        tb_txt = slide.shapes.add_textbox(Inches(3.20), top_kpi + Inches(0.10), kpi_w - Inches(2.50), kpi_h - Inches(0.20))
        tf_t = tb_txt.text_frame
        tf_t.word_wrap = True

        pt1 = tf_t.paragraphs[0]
        pt1.text = label
        pt1.font.name = FONT_HEADING
        pt1.font.size = Pt(8.5)
        pt1.font.bold = True
        pt1.font.color.rgb = COLOR_TEXT_HERO
        pt1.space_after = Pt(2)

        pt2 = tf_t.add_paragraph()
        pt2.text = desc
        pt2.font.name = FONT_BODY
        pt2.font.size = Pt(8.5)
        pt2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Card: Benchmark Chart
    right_left = Inches(0.8) + split_w + split_gap
    add_glass_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_CARD_ALT, border_color=COLOR_BORDER_MUTED, border_width=Pt(1))

    img_path = os.path.join(ASSETS_DIR, "fig_extractor_benchmark_chart.png")
    add_image_fit(slide, img_path, right_left + Inches(0.2), top_pos + Inches(0.2), split_w - Inches(0.4), split_h - Inches(0.8))

    tb_cap = slide.shapes.add_textbox(right_left + Inches(0.2), top_pos + split_h - Inches(0.55), split_w - Inches(0.4), Inches(0.45))
    tf_c = tb_cap.text_frame
    tf_c.word_wrap = True
    pc = tf_c.paragraphs[0]
    pc.text = "Figure 3: rPPG Extractor SNR & Model Error (MAE) Benchmark Comparison"
    pc.font.name = FONT_BODY
    pc.font.size = Pt(9)
    pc.font.italic = True
    pc.font.color.rgb = COLOR_TEXT_DIM
    pc.alignment = PP_ALIGN.CENTER

    return slide

def build_slide_11_grand_finale(prs):
    """Slide 11: Conclusion remarks & Future Scope of work (Grand Studio Finale)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_studio_bg(slide)
    add_header_banner(slide, "Slide 12: Conclusion remarks & Future Scope of work", "Summary & Capstone Roadmap", COLOR_NEON_AMBER)

    split_w = Inches(5.76)
    split_h = Inches(4.35)
    split_gap = Inches(0.20)
    top_pos = Inches(1.65)

    # Left Glass Card: Concluding Remarks
    add_glass_card(slide, Inches(0.8), top_pos, split_w, split_h, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))

    tb_left = slide.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.18), split_w - Inches(0.50), split_h - Inches(0.36))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p_tag1 = tf_l.paragraphs[0]
    p_tag1.text = "✦ CONCLUDING ACHIEVEMENTS"
    p_tag1.font.name = FONT_HEADING
    p_tag1.font.size = Pt(9)
    p_tag1.font.bold = True
    p_tag1.font.color.rgb = COLOR_NEON_CYAN
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
        r1.font.color.rgb = COLOR_TEXT_PRIMARY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Right Glass Card: Future Scope
    right_left = Inches(0.8) + split_w + split_gap
    add_glass_card(slide, right_left, top_pos, split_w, split_h, fill_color=COLOR_CARD_BG, border_color=COLOR_BORDER_AMBER, border_width=Pt(1))

    tb_right = slide.shapes.add_textbox(right_left + Inches(0.25), top_pos + Inches(0.18), split_w - Inches(0.50), split_h - Inches(0.36))
    tf_r = tb_right.text_frame
    tf_r.word_wrap = True

    p_tag2 = tf_r.paragraphs[0]
    p_tag2.text = "✦ FUTURE SCOPE & ROADMAP"
    p_tag2.font.name = FONT_HEADING
    p_tag2.font.size = Pt(9)
    p_tag2.font.bold = True
    p_tag2.font.color.rgb = COLOR_NEON_AMBER
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
        r1.font.color.rgb = COLOR_TEXT_PRIMARY

        r2 = pb.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = COLOR_TEXT_MUTED

    # Bottom Acknowledgement Banner
    bottom_top = top_pos + split_h + Inches(0.15)
    bottom_h = Inches(0.85)
    bottom_card = add_glass_card(slide, Inches(0.8), bottom_top, Inches(11.733), bottom_h, fill_color=COLOR_CARD_GLOW, border_color=COLOR_BORDER_CYAN, border_width=Pt(1))

    tb_bot = slide.shapes.add_textbox(Inches(1.0), bottom_top + Inches(0.10), Inches(11.333), Inches(0.65))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True

    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "Heartfelt Gratitude to Dr. Anurag Singh (IIIT-NR), Prof. Aparna Pandey (BIT Raipur), Faculty Members & Committee Reviewers"
    p_b1.font.name = FONT_HEADING
    p_b1.font.size = Pt(11)
    p_b1.font.bold = True
    p_b1.font.color.rgb = COLOR_TEXT_HERO
    p_b1.alignment = PP_ALIGN.CENTER
    p_b1.space_after = Pt(2)

    p_b2 = tf_b.add_paragraph()
    p_b2.text = "— Thank You  •  Open for Questions & Feedback —"
    p_b2.font.name = FONT_HEADING
    p_b2.font.size = Pt(10.5)
    p_b2.font.bold = True
    p_b2.font.color.rgb = COLOR_NEON_CYAN
    p_b2.alignment = PP_ALIGN.CENTER

    return slide

# =============================================================================
# 4. MAIN DECK GENERATOR
# =============================================================================

def build_all():
    print("============================================================")
    print("COMPILING ULTIMATE STUDIO PPT PRESENTATION DECK")
    print("============================================================")

    prs = create_presentation()

    print("Building Slide 1: Hero Launchpad Title Slide...")
    build_slide_1_hero_title(prs)

    print("Building Slide 2: Introduction about the training undergone...")
    build_slide_2_intro_pillars(prs)

    print("Building Slide 3: Training Objectives...")
    build_slide_3_objectives_stepper(prs)

    print("Building Slide 4: Training Modules / Topics Covered...")
    build_slide_4_curriculum_matrix(prs)

    print("Building Slide 5: Key Learnings...")
    build_slide_5_key_learnings(prs)

    print("Building Slide 6: Proposed Project Title & its Introduction...")
    build_slide_6_proposed_project(prs)

    print("Building Slide 7: Objectives of the Proposed Project...")
    build_slide_7_objectives_project(prs)

    print("Building Slide 8: Methodology / Approach of the Proposed Project...")
    build_slide_8_methodology(prs)

    print("Building Slide 9: Proposed Project Work Details & LIVE DEMO SPOTLIGHT...")
    build_slide_9_work_details_demo(prs)

    print("Building Slide 10: Expected Outcomes & Results (KPI Dashboard)...")
    build_slide_10_results_dashboard(prs)

    print("Building Slide 11: Conclusion remarks & Future Scope (Grand Finale)...")
    build_slide_11_grand_finale(prs)

    # Save outputs
    prs.save(FULL_OUTPUT)
    print(f"Saved primary deck to: {FULL_OUTPUT}")

    prs.save(STUDIO_OUTPUT)
    print(f"Saved studio deck to: {STUDIO_OUTPUT}")

    prs.save(DOWNLOADS_OUT)
    print(f"Saved update to Downloads: {DOWNLOADS_OUT}")

    print("============================================================")
    print("ALL 11 SLIDES COMPILED & SAVED WITH NATIVE TRANSITIONS!")
    print("============================================================")

if __name__ == "__main__":
    build_all()
