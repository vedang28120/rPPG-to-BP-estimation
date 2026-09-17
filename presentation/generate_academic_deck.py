r"""
generate_academic_deck.py
=========================
Premium Academic Presentation Generator

Design Philosophy: "Scholarly Elegance"
- Warm white canvas (#FAFAF8) with a subtle left-edge teal accent stripe
- Deep forest teal (#1B4332) as the primary heading color
- Warm gold (#B8860B) as the secondary accent for labels and highlights
- Soft cream content cards (#FFFFFF) with delicate drop shadows
- Clean sans-serif typography (Calibri headings, Calibri body)
- Generous whitespace, tight content blocks, no oversized empty containers
- Subtle decorative geometric shapes (thin accent lines, small circles)
- Smooth native PowerPoint "push" and "fade" slide transitions

NO: glassmorphism, neon, harsh gradients, em dashes, bento grids, purple/black.
"""

import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn

# ============================================================================
# DESIGN TOKENS
# ============================================================================

# Palette: Nature-inspired academic teal + warm gold
CANVAS          = RGBColor(250, 250, 248)   # #FAFAF8 Warm off-white
WHITE           = RGBColor(255, 255, 255)   # Pure white for cards
CARD_BG         = RGBColor(255, 255, 255)   # Card backgrounds

TEAL_DEEP       = RGBColor(27, 67, 50)      # #1B4332 Deep forest teal (headings)
TEAL_MID        = RGBColor(45, 106, 79)     # #2D6A4F Medium teal
TEAL_LIGHT      = RGBColor(64, 145, 108)    # #40916C Lighter teal
TEAL_PALE       = RGBColor(183, 228, 199)   # #B7E4C7 Very pale teal (backgrounds)
TEAL_WASH       = RGBColor(232, 246, 239)   # #E8F6EF Faintest teal wash

GOLD            = RGBColor(184, 134, 11)    # #B8860B Warm dark gold (accents)
GOLD_LIGHT      = RGBColor(218, 175, 71)    # #DAAF47 Lighter gold
GOLD_PALE       = RGBColor(253, 245, 225)   # #FDF5E1 Pale gold wash

TEXT_DARK       = RGBColor(33, 37, 41)      # #212529 Near-black body text
TEXT_BODY       = RGBColor(52, 58, 64)      # #343A40 Body text
TEXT_SECONDARY  = RGBColor(108, 117, 125)   # #6C757D Muted secondary
TEXT_LIGHT      = RGBColor(173, 181, 189)   # #ADB5BD Light text

BORDER_LIGHT    = RGBColor(222, 226, 230)   # #DEE2E6 Light border
BORDER_TEAL     = RGBColor(149, 213, 178)   # #95D5B2 Teal border (soft)

# Shadows (as hex for XML)
SHADOW_COLOR    = "000000"
SHADOW_ALPHA    = "18000"  # 18% opacity

# Typography
FONT_HEADING = "Calibri"
FONT_BODY    = "Calibri"

# Slide dimensions (16:9)
SW = 13.333
SH = 7.500

# Paths
WORKSPACE = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation"
ASSETS    = os.path.join(WORKSPACE, "presentation", "assets")
OUT_PRIMARY   = os.path.join(WORKSPACE, "presentation", "VT_2026_rPPG_to_BP_Estimation.pptx")
OUT_ACADEMIC  = os.path.join(WORKSPACE, "presentation", "VT_2026_Academic_Deck.pptx")
OUT_DOWNLOADS = r"C:\Users\simpl\Downloads\Sample PPT _VT 2026.pptx"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_prs():
    prs = Presentation()
    prs.slide_width = Inches(SW)
    prs.slide_height = Inches(SH)
    return prs

def set_canvas_bg(slide):
    """Set warm off-white background and add native fade transition."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = CANVAS
    # Native fade transition
    try:
        trans = parse_xml(f'<p:transition {nsdecls("p")} spd="med" advClick="1"><p:fade/></p:transition>')
        slide._element.append(trans)
    except:
        pass

def add_left_accent_stripe(slide, color1_hex="1B4332", color2_hex="2D6A4F", width=0.35):
    """Add a thin gradient accent stripe along the left edge."""
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(width), Inches(SH)
    )
    spPr = stripe._element.find(qn('p:spPr'))
    # Remove existing fill
    for child in list(spPr):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('solidFill', 'noFill', 'gradFill'):
            spPr.remove(child)
    # Add gradient
    grad = parse_xml(
        f'<a:gradFill {nsdecls("a")} rotWithShape="0">'
        f'  <a:gsLst>'
        f'    <a:gs pos="0"><a:srgbClr val="{color1_hex}"/></a:gs>'
        f'    <a:gs pos="100000"><a:srgbClr val="{color2_hex}"/></a:gs>'
        f'  </a:gsLst>'
        f'  <a:lin ang="5400000" scaled="1"/>'
        f'</a:gradFill>'
    )
    ln = spPr.find(qn('a:ln'))
    if ln is not None:
        spPr.insert(list(spPr).index(ln), grad)
    else:
        spPr.append(grad)
    stripe.line.fill.background()
    return stripe

def add_top_accent_line(slide, left, top, width, color=TEAL_MID, thickness=Pt(2.5)):
    """Add a thin horizontal accent line."""
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, thickness)
    line.fill.solid()
    line.fill.fore_color.rgb = color
    line.line.fill.background()
    return line

def add_card(slide, left, top, width, height, shadow=True, border_color=None):
    """Add a white card with optional soft shadow and border."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.color.rgb = BORDER_LIGHT
        card.line.width = Pt(0.75)
    
    if shadow:
        spPr = card._element.find(qn('p:spPr'))
        shadow_xml = parse_xml(
            f'<a:effectLst {nsdecls("a")}>'
            f'  <a:outerShdw blurRad="50000" dist="25000" dir="5400000" rotWithShape="0">'
            f'    <a:srgbClr val="{SHADOW_COLOR}"><a:alpha val="{SHADOW_ALPHA}"/></a:srgbClr>'
            f'  </a:outerShdw>'
            f'</a:effectLst>'
        )
        spPr.append(shadow_xml)
    
    return card

def add_teal_pill(slide, left, top, width, text, font_size=Pt(8)):
    """Small teal pill/badge for labels."""
    pill_h = Inches(0.28)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, pill_h)
    pill.fill.solid()
    pill.fill.fore_color.rgb = TEAL_DEEP
    pill.line.fill.background()
    
    tf = pill.text_frame
    tf.word_wrap = False
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    tf.margin_top = Pt(1)
    tf.margin_bottom = Pt(1)
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_HEADING
    p.font.size = font_size
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    return pill

def add_gold_pill(slide, left, top, width, text, font_size=Pt(8)):
    """Small gold pill/badge for category labels."""
    pill_h = Inches(0.28)
    pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, pill_h)
    pill.fill.solid()
    pill.fill.fore_color.rgb = GOLD
    pill.line.fill.background()
    
    tf = pill.text_frame
    tf.word_wrap = False
    tf.margin_left = Pt(6)
    tf.margin_right = Pt(6)
    tf.margin_top = Pt(1)
    tf.margin_bottom = Pt(1)
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = FONT_HEADING
    p.font.size = font_size
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER
    return pill

def add_number_circle(slide, left, top, number, size=Inches(0.42), bg_color=TEAL_DEEP, text_color=WHITE):
    """Small numbered circle for step indicators."""
    circ = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, size, size)
    circ.fill.solid()
    circ.fill.fore_color.rgb = bg_color
    circ.line.fill.background()
    
    tf = circ.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = str(number)
    p.font.name = FONT_HEADING
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = text_color
    p.alignment = PP_ALIGN.CENTER
    return circ

def add_textbox(slide, left, top, width, height):
    """Add textbox and return text_frame."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    return tf

def set_para(tf, text, font_size=Pt(10), bold=False, color=TEXT_BODY, align=PP_ALIGN.LEFT, space_after=Pt(4), font_name=None, is_first=True, italic=False):
    """Set or add a paragraph with given styling."""
    if is_first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = text
    p.font.name = font_name or FONT_BODY
    p.font.size = font_size
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    p.alignment = align
    p.space_after = space_after
    return p

def add_rich_bullet(tf, label, desc, is_first=False, label_color=TEAL_DEEP, desc_color=TEXT_BODY, label_size=Pt(10), desc_size=Pt(9.5), space_after=Pt(6)):
    """Add a bullet with bold label and regular description using runs."""
    if is_first:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.space_after = space_after
    
    r1 = p.add_run()
    r1.text = f"\u2022 {label} "
    r1.font.name = FONT_HEADING
    r1.font.size = label_size
    r1.font.bold = True
    r1.font.color.rgb = label_color
    
    r2 = p.add_run()
    r2.text = desc
    r2.font.name = FONT_BODY
    r2.font.size = desc_size
    r2.font.color.rgb = desc_color
    return p

def add_image_fit(slide, img_path, box_left, box_top, box_width, box_height):
    """Aspect-ratio preserving image placement."""
    if not os.path.exists(img_path):
        return None
    with Image.open(img_path) as im:
        img_w, img_h = im.size
    img_aspect = img_w / img_h
    b_l, b_t, b_w, b_h = float(box_left), float(box_top), float(box_width), float(box_height)
    box_aspect = b_w / b_h
    if img_aspect > box_aspect:
        final_w = b_w
        final_h = b_w / img_aspect
        final_l = b_l
        final_t = b_t + (b_h - final_h) / 2.0
    else:
        final_h = b_h
        final_w = b_h * img_aspect
        final_t = b_t
        final_l = b_l + (b_w - final_w) / 2.0
    return slide.shapes.add_picture(img_path, int(final_l), int(final_t), int(final_w), int(final_h))

def add_slide_number(slide, num, total=11):
    """Add a subtle slide number at bottom right."""
    tf = add_textbox(slide, Inches(SW - 1.5), Inches(SH - 0.40), Inches(1.2), Inches(0.25))
    set_para(tf, f"{num} / {total}", font_size=Pt(8), color=TEXT_LIGHT, align=PP_ALIGN.RIGHT, space_after=Pt(0))

def add_bottom_bar(slide):
    """Add a thin teal bar at the very bottom."""
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(SH - 0.06), Inches(SW), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL_DEEP
    bar.line.fill.background()

def build_header_area(slide, slide_label, title, slide_num, total=11):
    """Consistent header across all content slides (2-11)."""
    add_left_accent_stripe(slide)
    
    # Slide label pill
    add_teal_pill(slide, Inches(0.65), Inches(0.35), Inches(1.3), slide_label, font_size=Pt(7.5))
    
    # Title
    tf = add_textbox(slide, Inches(0.65), Inches(0.68), Inches(11.5), Inches(0.45))
    set_para(tf, title, font_size=Pt(20), bold=True, color=TEAL_DEEP, font_name=FONT_HEADING, space_after=Pt(0))
    
    # Accent underline
    add_top_accent_line(slide, Inches(0.65), Inches(1.18), Inches(2.5), color=GOLD, thickness=Pt(2.5))
    
    # Thin separator extending further
    add_top_accent_line(slide, Inches(3.20), Inches(1.18), Inches(9.48), color=BORDER_LIGHT, thickness=Pt(0.75))
    
    add_slide_number(slide, slide_num, total)
    add_bottom_bar(slide)


# ============================================================================
# SLIDE BUILDERS
# ============================================================================

def slide_01_title(prs):
    """SLIDE 1: Title Slide with elegant teal gradient header band."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    
    # Top gradient band (teal)
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(SW), Inches(2.6))
    spPr = band._element.find(qn('p:spPr'))
    for child in list(spPr):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
        if tag in ('solidFill', 'noFill', 'gradFill'):
            spPr.remove(child)
    grad = parse_xml(
        f'<a:gradFill {nsdecls("a")} rotWithShape="0">'
        f'  <a:gsLst>'
        f'    <a:gs pos="0"><a:srgbClr val="1B4332"/></a:gs>'
        f'    <a:gs pos="60000"><a:srgbClr val="2D6A4F"/></a:gs>'
        f'    <a:gs pos="100000"><a:srgbClr val="40916C"/></a:gs>'
        f'  </a:gsLst>'
        f'  <a:lin ang="0" scaled="1"/>'
        f'</a:gradFill>'
    )
    ln = spPr.find(qn('a:ln'))
    if ln is not None:
        spPr.insert(list(spPr).index(ln), grad)
    else:
        spPr.append(grad)
    band.line.fill.background()
    
    # Gold accent line at bottom of band
    gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(2.6), Inches(SW), Pt(3))
    gold_line.fill.solid()
    gold_line.fill.fore_color.rgb = GOLD
    gold_line.line.fill.background()
    
    # Logo in white card frame (top-left)
    logo_path = os.path.join(ASSETS, "image1.jpeg")
    logo_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(0.35), Inches(1.30), Inches(1.30))
    logo_card.fill.solid()
    logo_card.fill.fore_color.rgb = WHITE
    logo_card.line.fill.background()
    # Shadow on logo card
    spPr_logo = logo_card._element.find(qn('p:spPr'))
    shadow_xml = parse_xml(
        f'<a:effectLst {nsdecls("a")}>'
        f'  <a:outerShdw blurRad="40000" dist="15000" dir="5400000" rotWithShape="0">'
        f'    <a:srgbClr val="000000"><a:alpha val="20000"/></a:srgbClr>'
        f'  </a:outerShdw>'
        f'</a:effectLst>'
    )
    spPr_logo.append(shadow_xml)
    if os.path.exists(logo_path):
        add_image_fit(slide, logo_path, Inches(0.72), Inches(0.42), Inches(1.16), Inches(1.16))
    
    # Header text on teal band
    tf_header = add_textbox(slide, Inches(2.20), Inches(0.35), Inches(10.5), Inches(0.50))
    set_para(tf_header, "A Presentation on Vocational Training & Proposed Project", font_size=Pt(11), bold=False, color=RGBColor(183, 228, 199), align=PP_ALIGN.LEFT, space_after=Pt(0))
    
    # Main title on band
    tf_title = add_textbox(slide, Inches(2.20), Inches(0.82), Inches(10.5), Inches(0.80))
    set_para(tf_title, "Mobile Remote Photoplethysmography to\nCuffless Blood Pressure Estimation", font_size=Pt(22), bold=True, color=WHITE, font_name=FONT_HEADING, space_after=Pt(0))
    
    # Training subtitle
    tf_sub = add_textbox(slide, Inches(2.20), Inches(1.72), Inches(10.5), Inches(0.40))
    p_sub = tf_sub.paragraphs[0]
    r1 = p_sub.add_run()
    r1.text = "AI with Python "
    r1.font.name = FONT_HEADING
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = GOLD_LIGHT
    r2 = p_sub.add_run()
    r2.text = "  |  IIIT Naya Raipur  |  01 July to 10 August 2026"
    r2.font.name = FONT_BODY
    r2.font.size = Pt(11)
    r2.font.color.rgb = RGBColor(183, 228, 199)
    
    # Content area below band: 3 information cards
    card_w = Inches(3.77)
    card_gap = Inches(0.20)
    card_top = Inches(2.95)
    card_h = Inches(2.05)
    
    # Card 1: Student Researchers
    c1_left = Inches(0.65)
    add_card(slide, c1_left, card_top, card_w, card_h, border_color=BORDER_TEAL)
    add_teal_pill(slide, c1_left + Inches(0.15), card_top + Inches(0.15), Inches(1.8), "STUDENT RESEARCHERS")
    
    tf_s = add_textbox(slide, c1_left + Inches(0.20), card_top + Inches(0.55), card_w - Inches(0.40), Inches(1.70))
    for i, (name, is_f) in enumerate([("Vedang Bhatt", True), ("Anubhav Shrivastav", False), ("Aadarsh", False)]):
        p = tf_s.paragraphs[0] if is_f else tf_s.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{i+1}. {name}"
        r1.font.name = FONT_HEADING
        r1.font.size = Pt(11)
        r1.font.bold = True
        r1.font.color.rgb = TEXT_DARK
        r2 = p.add_run()
        r2.text = "   B.Tech CSE, 4th Semester"
        r2.font.name = FONT_BODY
        r2.font.size = Pt(9)
        r2.font.color.rgb = TEXT_SECONDARY
        p.space_after = Pt(5)
    
    # Card 2: Mentors & Guidance
    c2_left = c1_left + card_w + card_gap
    add_card(slide, c2_left, card_top, card_w, card_h, border_color=BORDER_TEAL)
    add_gold_pill(slide, c2_left + Inches(0.15), card_top + Inches(0.15), Inches(2.0), "MENTORS & GUIDANCE")
    
    tf_m = add_textbox(slide, c2_left + Inches(0.20), card_top + Inches(0.55), card_w - Inches(0.40), Inches(1.70))
    
    p_m1l = tf_m.paragraphs[0]
    p_m1l.text = "VT Mentor (IIIT-NR)"
    p_m1l.font.name = FONT_BODY
    p_m1l.font.size = Pt(8.5)
    p_m1l.font.color.rgb = TEXT_SECONDARY
    p_m1l.space_after = Pt(1)
    
    set_para(tf_m, "Dr. Anurag Singh", font_size=Pt(12), bold=True, color=TEXT_DARK, is_first=False, space_after=Pt(10))
    
    p_m2l = tf_m.add_paragraph()
    p_m2l.text = "College Mentor (BIT Raipur)"
    p_m2l.font.name = FONT_BODY
    p_m2l.font.size = Pt(8.5)
    p_m2l.font.color.rgb = TEXT_SECONDARY
    p_m2l.space_after = Pt(1)
    
    set_para(tf_m, "Prof. Aparna Pandey", font_size=Pt(12), bold=True, color=TEXT_DARK, is_first=False, space_after=Pt(0))
    
    # Card 3: Department
    c3_left = c2_left + card_w + card_gap
    add_card(slide, c3_left, card_top, card_w, card_h, border_color=BORDER_TEAL)
    add_teal_pill(slide, c3_left + Inches(0.15), card_top + Inches(0.15), Inches(2.2), "ACADEMIC DEPARTMENT")
    
    tf_d = add_textbox(slide, c3_left + Inches(0.20), card_top + Inches(0.55), card_w - Inches(0.40), Inches(1.70))
    set_para(tf_d, "Department of Computer Science & Engineering", font_size=Pt(11), bold=True, color=TEXT_DARK, space_after=Pt(4))
    set_para(tf_d, "Bhilai Institute of Technology, Raipur", font_size=Pt(10), color=TEXT_BODY, is_first=False, space_after=Pt(2))
    set_para(tf_d, "Affiliated to CSVTU, Bhilai", font_size=Pt(9), color=TEXT_SECONDARY, is_first=False, space_after=Pt(0))
    
    # Bottom acknowledgement strip
    ack_top = Inches(5.60)
    ack_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), ack_top, Inches(11.93), Inches(0.70))
    ack_card.fill.solid()
    ack_card.fill.fore_color.rgb = TEAL_WASH
    ack_card.line.color.rgb = BORDER_TEAL
    ack_card.line.width = Pt(0.75)
    
    tf_ack = add_textbox(slide, Inches(0.85), ack_top + Inches(0.10), Inches(11.53), Inches(0.50))
    set_para(tf_ack, "We express our sincere gratitude to Dr. Anurag Singh (IIIT-NR), Prof. Aparna Pandey (BIT Raipur), and all faculty members for their invaluable guidance and support throughout this training.", font_size=Pt(9.5), color=TEAL_DEEP, align=PP_ALIGN.CENTER, italic=True, space_after=Pt(0))
    
    # Bottom bar and slide number
    add_bottom_bar(slide)
    add_slide_number(slide, 1)
    
    return slide


def slide_02_introduction(prs):
    """SLIDE 2: Introduction about the training undergone."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 2", "Introduction about the Training Undergone", 2)
    
    # 3 horizontal cards
    card_w = Inches(3.77)
    card_gap = Inches(0.20)
    card_top = Inches(1.55)
    card_h = Inches(4.80)
    
    cards_data = [
        {
            "num": "01",
            "title": "Academic Immersion",
            "subtitle": "6-Week Intensive at IIIT-NR",
            "color": TEAL_DEEP,
            "pill_color": "teal",
            "bullets": [
                ("Duration:", "01/07/2026 to 10/08/2026, full-time immersive training during summer break after 4th semester."),
                ("Course:", "'AI with Python', covering the complete spectrum from scientific computing to modern generative AI."),
                ("Mentorship:", "Expert guidance from Dr. Anurag Singh at IIIT-NR, with continuous laboratory and project support."),
                ("Environment:", "Advanced computational laboratory with hands-on coding sessions and live demonstrations.")
            ]
        },
        {
            "num": "02",
            "title": "Progressive Curriculum",
            "subtitle": "From Foundations to Deep Learning",
            "color": TEAL_MID,
            "pill_color": "teal",
            "bullets": [
                ("Data Foundations:", "NumPy vectorization, Pandas data wrangling, Matplotlib visualization, and preprocessing workflows."),
                ("Classical ML:", "Supervised and unsupervised learning paradigms, bias-variance analysis, L1/L2 regularization, K-fold validation."),
                ("Deep Learning:", "TensorFlow graph execution, activations (Sigmoid, ReLU, SoftMax), backpropagation, CNNs, RNNs, and LSTMs."),
                ("Signal Processing:", "Savitzky-Golay digital polynomial smoothing for noise reduction while preserving signal morphology.")
            ]
        },
        {
            "num": "03",
            "title": "Applied Capstone Bridge",
            "subtitle": "Training to Real-World Impact",
            "color": GOLD,
            "pill_color": "gold",
            "bullets": [
                ("Modern AI:", "Introductory exposure to NLP, Word2Vec, GloVe, Transformer Encoders, RAG, LangChain, and MCP."),
                ("Project Inspiration:", "Formulated a capstone bridging digital signal processing with contactless cardiovascular vital sensing."),
                ("Privacy-First:", "Designed for 100% on-device edge execution, ensuring no sensitive biometric data leaves the phone."),
                ("Honest Exploration:", "We approach this work as student explorers, acknowledging the boundaries of our prototyping.")
            ]
        }
    ]
    
    for i, cd in enumerate(cards_data):
        c_left = Inches(0.65) + i * (card_w + card_gap)
        bc = BORDER_TEAL if cd["pill_color"] == "teal" else RGBColor(218, 175, 71)
        add_card(slide, c_left, card_top, card_w, card_h, border_color=bc)
        
        # Number circle
        add_number_circle(slide, c_left + Inches(0.18), card_top + Inches(0.18), cd["num"], bg_color=cd["color"])
        
        # Title block
        tf_t = add_textbox(slide, c_left + Inches(0.70), card_top + Inches(0.15), card_w - Inches(0.88), Inches(0.60))
        set_para(tf_t, cd["title"], font_size=Pt(13), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, space_after=Pt(1))
        set_para(tf_t, cd["subtitle"], font_size=Pt(9), color=TEXT_SECONDARY, is_first=False, space_after=Pt(0))
        
        # Divider
        add_top_accent_line(slide, c_left + Inches(0.18), card_top + Inches(0.82), card_w - Inches(0.36), color=BORDER_LIGHT, thickness=Pt(0.75))
        
        # Bullets
        tf_b = add_textbox(slide, c_left + Inches(0.22), card_top + Inches(0.95), card_w - Inches(0.44), card_h - Inches(1.10))
        for j, (label, desc) in enumerate(cd["bullets"]):
            add_rich_bullet(tf_b, label, desc, is_first=(j==0), label_color=cd["color"], space_after=Pt(8))
    
    return slide


def slide_03_objectives(prs):
    """SLIDE 3: Training Objectives (5 horizontal milestone rows)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 3", "Training Objectives", 3)
    
    row_h = Inches(0.92)
    row_gap = Inches(0.12)
    start_top = Inches(1.55)
    row_w = Inches(11.93)
    
    milestones = [
        ("1", "Python & Scientific Data Foundations", "Build strong fluency in Python for data science, vectorized computation (NumPy), and exploratory data manipulation (Pandas, Matplotlib).", TEAL_DEEP),
        ("2", "Machine Learning & Validation Rigor", "Understand supervised/unsupervised algorithms, bias-variance tradeoffs, L1/L2 regularization, and robust K-Fold cross-validation with precision/recall/F1.", TEAL_MID),
        ("3", "Deep Learning & Neural Architectures", "Master neural network mechanics (activations, backpropagation) and implement CNNs, RNNs, LSTMs, and Self-Attention layers in TensorFlow.", TEAL_LIGHT),
        ("4", "Signal Processing & Vector Operations", "Implement digital smoothing techniques such as Savitzky-Golay filtering for noise reduction and learn vector space metrics (Cosine Similarity).", GOLD),
        ("5", "NLP, Transformers & Agentic AI", "Gain introductory exposure to Word2Vec/GloVe, Transformer encoders, RAG architectures, LangChain, Agentic AI tools, and Model Context Protocol.", GOLD)
    ]
    
    for i, (num, title, desc, accent) in enumerate(milestones):
        top = start_top + i * (row_h + row_gap)
        add_card(slide, Inches(0.65), top, row_w, row_h)
        
        # Left accent bar on card
        accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), top, Inches(0.06), row_h)
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = accent
        accent_bar.line.fill.background()
        
        add_number_circle(slide, Inches(0.88), top + Inches(0.25), num, bg_color=accent)
        
        tf = add_textbox(slide, Inches(1.45), top + Inches(0.12), row_w - Inches(1.0), row_h - Inches(0.24))
        set_para(tf, title, font_size=Pt(12), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, space_after=Pt(3))
        set_para(tf, desc, font_size=Pt(9.5), color=TEXT_BODY, is_first=False, space_after=Pt(0))
    
    return slide


def slide_04_curriculum(prs):
    """SLIDE 4: Training Modules / Topics Covered (5 compact vertical cards)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 4", "Training Modules / Topics Covered", 4)
    
    col_w = Inches(2.28)
    col_gap = Inches(0.12)
    col_top = Inches(1.55)
    col_h = Inches(4.80)
    
    modules = [
        {
            "label": "MODULE 1",
            "title": "Python & Data",
            "accent": TEAL_DEEP,
            "topics": [
                "Python fundamentals",
                "NumPy vectorization",
                "Pandas data wrangling",
                "Matplotlib visualization",
                "Data preprocessing",
                "Feature scaling & norms"
            ]
        },
        {
            "label": "MODULE 2",
            "title": "Machine Learning",
            "accent": TEAL_MID,
            "topics": [
                "Supervised & Unsupervised",
                "Semi-supervised & RL",
                "Linear & Polynomial Reg.",
                "Logistic Regression",
                "Bias-Variance tradeoff",
                "L1/L2 Regularization",
                "K-Fold cross-validation",
                "Accuracy, Prec, Recall, F1"
            ]
        },
        {
            "label": "MODULE 3",
            "title": "Deep Learning",
            "accent": TEAL_LIGHT,
            "topics": [
                "TensorFlow ecosystem",
                "Computational graphs",
                "Backpropagation",
                "Sigmoid, ReLU, SoftMax",
                "Conv, Pool, Dense layers",
                "CNN architectures",
                "RNN & LSTM models",
                "Self-Attention primitives"
            ]
        },
        {
            "label": "MODULE 4",
            "title": "Signal & NLP",
            "accent": GOLD,
            "topics": [
                "Savitzky-Golay filter",
                "NLP with NLTK",
                "Word2Vec embeddings",
                "GloVe representations",
                "Contextual embeddings",
                "Sequence encoders",
                "Cosine Similarity"
            ]
        },
        {
            "label": "MODULE 5",
            "title": "GenAI & Agents",
            "accent": GOLD,
            "topics": [
                "Transformer architecture",
                "Tokens & Tokenization",
                "Large Language Models",
                "Fine-tuning open models",
                "RAG architecture",
                "LangChain orchestration",
                "Agentic AI & tool calling",
                "MCP (Model Context Protocol)"
            ]
        }
    ]
    
    for i, m in enumerate(modules):
        c_left = Inches(0.65) + i * (col_w + col_gap)
        bc = BORDER_TEAL if m["accent"] != GOLD else RGBColor(218, 175, 71)
        add_card(slide, c_left, col_top, col_w, col_h, border_color=bc)
        
        # Top colored strip
        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, col_top, col_w, Inches(0.05))
        strip.fill.solid()
        strip.fill.fore_color.rgb = m["accent"]
        strip.line.fill.background()
        
        # Module label + title
        tf_h = add_textbox(slide, c_left + Inches(0.12), col_top + Inches(0.14), col_w - Inches(0.24), Inches(0.50))
        set_para(tf_h, m["label"], font_size=Pt(8), bold=True, color=m["accent"], space_after=Pt(1))
        set_para(tf_h, m["title"], font_size=Pt(11), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, is_first=False, space_after=Pt(0))
        
        # Divider
        add_top_accent_line(slide, c_left + Inches(0.12), col_top + Inches(0.70), col_w - Inches(0.24), color=BORDER_LIGHT, thickness=Pt(0.75))
        
        # Topics
        tf_t = add_textbox(slide, c_left + Inches(0.12), col_top + Inches(0.80), col_w - Inches(0.24), col_h - Inches(0.90))
        for j, topic in enumerate(m["topics"]):
            p = tf_t.paragraphs[0] if j == 0 else tf_t.add_paragraph()
            p.text = f"\u2022  {topic}"
            p.font.name = FONT_BODY
            p.font.size = Pt(9)
            p.font.color.rgb = TEXT_BODY
            p.space_after = Pt(4)
    
    return slide


def slide_05_key_learnings(prs):
    """SLIDE 5: Key Learnings (2x2 card grid)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 5", "Key Learnings", 5)
    
    card_w = Inches(5.87)
    card_h = Inches(2.30)
    card_gap_x = Inches(0.20)
    card_gap_y = Inches(0.18)
    top_r1 = Inches(1.55)
    top_r2 = top_r1 + card_h + card_gap_y
    
    learnings = [
        ("01", "PREPROCESSING & VALIDATION", "Real-world signals carry severe baseline wander and sensor noise. Standardizing feature distributions, robust encoding, and using K-fold cross-validation are essential before training any neural network.", TEAL_DEEP, Inches(0.65), top_r1),
        ("02", "DIGITAL SIGNAL FILTERING", "Learning the Savitzky-Golay filter demonstrated how local polynomial regression effectively removes high-frequency noise while preserving vital systolic/diastolic peak extrema in physiological signals.", TEAL_MID, Inches(0.65) + card_w + card_gap_x, top_r1),
        ("03", "CONVOLUTIONAL + SEQUENTIAL SYNERGY", "Combining 1D convolutions (for localized morphological features) with recurrent and self-attention layers (for temporal cardiac periodicity) provides a powerful time-series regression framework.", TEAL_LIGHT, Inches(0.65), top_r2),
        ("04", "CAPSTONE INSPIRATION", "Guided by our coursework in Python, signal processing, and deep neural models, we formulated our capstone: extracting optical pulse signals from smartphone cameras for cuffless blood pressure estimation.", GOLD, Inches(0.65) + card_w + card_gap_x, top_r2)
    ]
    
    for num, tag, desc, accent, left, top in learnings:
        add_card(slide, left, top, card_w, card_h)
        
        # Left accent
        ab = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.06), card_h)
        ab.fill.solid()
        ab.fill.fore_color.rgb = accent
        ab.line.fill.background()
        
        # Number + Tag row
        add_number_circle(slide, left + Inches(0.22), top + Inches(0.20), num, bg_color=accent, size=Inches(0.38))
        
        tf_tag = add_textbox(slide, left + Inches(0.70), top + Inches(0.20), card_w - Inches(1.0), Inches(0.30))
        set_para(tf_tag, tag, font_size=Pt(9), bold=True, color=accent, font_name=FONT_HEADING, space_after=Pt(0))
        
        # Description
        tf_desc = add_textbox(slide, left + Inches(0.22), top + Inches(0.65), card_w - Inches(0.44), card_h - Inches(0.85))
        set_para(tf_desc, desc, font_size=Pt(10), color=TEXT_BODY, space_after=Pt(0))
    
    return slide


def slide_06_project_intro(prs):
    """SLIDE 6: Proposed Project Title & Introduction (2-column split)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 6", "Proposed Project Title & its Introduction", 6)
    
    half_w = Inches(5.87)
    half_h = Inches(4.95)
    gap = Inches(0.20)
    top = Inches(1.55)
    
    # Left card: Project description
    add_card(slide, Inches(0.65), top, half_w, half_h, border_color=BORDER_TEAL)
    
    # Project title highlight box
    title_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), top + Inches(0.15), half_w - Inches(0.40), Inches(0.75))
    title_box.fill.solid()
    title_box.fill.fore_color.rgb = TEAL_WASH
    title_box.line.color.rgb = BORDER_TEAL
    title_box.line.width = Pt(0.75)
    
    tf_pt = add_textbox(slide, Inches(1.00), top + Inches(0.22), half_w - Inches(0.70), Inches(0.60))
    set_para(tf_pt, "Mobile Remote Photoplethysmography (rPPG)\nto Cuffless Blood Pressure Estimation", font_size=Pt(12), bold=True, color=TEAL_DEEP, font_name=FONT_HEADING, space_after=Pt(0))
    
    # Motivation bullets
    tf_b = add_textbox(slide, Inches(0.85), top + Inches(1.05), half_w - Inches(0.40), half_h - Inches(1.20))
    
    add_gold_pill(slide, Inches(0.85), top + Inches(1.05), Inches(1.8), "CLINICAL CONTEXT")
    
    bullets = [
        ("Global Challenge:", "Hypertension impacts over 1.28 billion adults globally as a primary asymptomatic cardiovascular risk factor."),
        ("Cuff Limitations:", "Traditional inflatable cuffs are intermittent, uncomfortable, and unsuitable for continuous monitoring or sleep studies."),
        ("White-Coat Effect:", "In-clinic measurements induce acute stress, frequently producing elevated false-positive readings."),
        ("Contactless Concept:", "Smartphone RGB cameras can detect subtle facial color variations caused by blood volume pulses, enabling non-invasive continuous estimation.")
    ]
    
    tf_b2 = add_textbox(slide, Inches(0.85), top + Inches(1.45), half_w - Inches(0.40), half_h - Inches(1.60))
    for j, (label, desc) in enumerate(bullets):
        add_rich_bullet(tf_b2, label, desc, is_first=(j==0), space_after=Pt(8))
    
    # Right card: Figure
    right_left = Inches(0.65) + half_w + gap
    add_card(slide, right_left, top, half_w, half_h)
    
    add_teal_pill(slide, right_left + Inches(0.18), top + Inches(0.15), Inches(2.5), "HEMODYNAMIC MODEL")
    
    img_path = os.path.join(ASSETS, "fig_windkessel_damping.png")
    add_image_fit(slide, img_path, right_left + Inches(0.20), top + Inches(0.55), half_w - Inches(0.40), half_h - Inches(1.15))
    
    tf_cap = add_textbox(slide, right_left + Inches(0.20), top + half_h - Inches(0.50), half_w - Inches(0.40), Inches(0.40))
    set_para(tf_cap, "Transcutaneous optical absorption & hemodynamic waveform dynamics", font_size=Pt(8.5), color=TEXT_SECONDARY, align=PP_ALIGN.CENTER, italic=True, space_after=Pt(0))
    
    return slide


def slide_07_objectives_project(prs):
    """SLIDE 7: Objectives of the Proposed Project (5 rows)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 7", "Objectives of the Proposed Project", 7)
    
    row_h = Inches(0.92)
    row_gap = Inches(0.12)
    start_top = Inches(1.55)
    row_w = Inches(11.93)
    
    objectives = [
        ("1", "Optical Pulse Extraction", "Capture facial video via smartphone camera and extract rPPG pulse waveforms using ROI localization and POS chrominance projection.", TEAL_DEEP),
        ("2", "Physiological Signal Filtering", "Apply bandpass filtering and Savitzky-Golay polynomial smoothing to isolate cardiac harmonics in the 0.75 to 2.5 Hz band.", TEAL_MID),
        ("3", "Deep Neural Sequence Regression", "Develop a hybrid architecture (1D-CNN + BiGRU + Self-Attention) in TensorFlow to estimate SBP and DBP from pulse waveforms.", TEAL_LIGHT),
        ("4", "Personal Calibration Study", "Investigate single-point baseline calibration to anchor individual vascular tone and arterial stiffness variations.", GOLD),
        ("5", "Edge Mobile Inference", "Assess on-device inference feasibility for privacy-preserving mobile execution using lightweight quantized models.", GOLD)
    ]
    
    for i, (num, title, desc, accent) in enumerate(objectives):
        top = start_top + i * (row_h + row_gap)
        add_card(slide, Inches(0.65), top, row_w, row_h)
        
        ab = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), top, Inches(0.06), row_h)
        ab.fill.solid()
        ab.fill.fore_color.rgb = accent
        ab.line.fill.background()
        
        add_number_circle(slide, Inches(0.88), top + Inches(0.25), num, bg_color=accent)
        
        tf = add_textbox(slide, Inches(1.45), top + Inches(0.12), row_w - Inches(1.0), row_h - Inches(0.24))
        set_para(tf, title, font_size=Pt(12), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, space_after=Pt(3))
        set_para(tf, desc, font_size=Pt(9.5), color=TEXT_BODY, is_first=False, space_after=Pt(0))
    
    return slide


def slide_08_methodology(prs):
    """SLIDE 8: Methodology / Approach (2-column: pipeline text + diagram)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 9", "Methodology / Approach of the Proposed Project", 8)
    
    half_w = Inches(5.87)
    half_h = Inches(4.95)
    gap = Inches(0.20)
    top = Inches(1.55)
    
    # Left card: 5 pipeline stages
    add_card(slide, Inches(0.65), top, half_w, half_h, border_color=BORDER_TEAL)
    add_teal_pill(slide, Inches(0.85), top + Inches(0.15), Inches(2.5), "5-STAGE PIPELINE")
    
    tf = add_textbox(slide, Inches(0.85), top + Inches(0.55), half_w - Inches(0.40), half_h - Inches(0.70))
    
    stages = [
        ("Stage 0  |  Sensor Lock:", "Camera2 API explicit sensor lock (ISO gain, fixed exposure) to eliminate auto-exposure oscillations."),
        ("Stage 1  |  Facial ROI Tracking:", "Facial landmark tracking to dynamically isolate perfused forehead skin pixels."),
        ("Stage 2  |  Chrominance Projection:", "Plane-Orthogonal-to-Skin (POS) color subspace projection to cancel specular reflections (8.9 dB SNR)."),
        ("Stage 3  |  DSP Filtering:", "Resample to 125 Hz via PCHIP, Butterworth bandpass (0.75 to 2.5 Hz), Savitzky-Golay polynomial smoothing."),
        ("Stage 4  |  Deep Regression:", "Sequence-to-value regression model extracting morphological pulse features for SBP/DBP prediction.")
    ]
    
    for j, (label, desc) in enumerate(stages):
        add_rich_bullet(tf, label, desc, is_first=(j==0), label_color=TEAL_DEEP, space_after=Pt(10))
    
    # Right card: Diagram
    right_left = Inches(0.65) + half_w + gap
    add_card(slide, right_left, top, half_w, half_h)
    add_teal_pill(slide, right_left + Inches(0.18), top + Inches(0.15), Inches(2.5), "PIPELINE DIAGRAM")
    
    img_path = os.path.join(ASSETS, "fig_pipeline_overview.png")
    add_image_fit(slide, img_path, right_left + Inches(0.20), top + Inches(0.55), half_w - Inches(0.40), half_h - Inches(1.10))
    
    tf_cap = add_textbox(slide, right_left + Inches(0.20), top + half_h - Inches(0.50), half_w - Inches(0.40), Inches(0.40))
    set_para(tf_cap, "End-to-end smartphone ingestion and deep sequence inference workflow", font_size=Pt(8.5), color=TEXT_SECONDARY, align=PP_ALIGN.CENTER, italic=True, space_after=Pt(0))
    
    return slide


def slide_09_work_details_demo(prs):
    """SLIDE 9: Proposed Project Work Details & Live Demo."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 10", "Proposed Project Work Details", 9)
    
    half_w = Inches(5.87)
    half_h = Inches(5.15)
    gap = Inches(0.20)
    top = Inches(1.55)
    
    # Left card: Architecture details
    add_card(slide, Inches(0.65), top, half_w, half_h, border_color=BORDER_TEAL)
    add_teal_pill(slide, Inches(0.85), top + Inches(0.15), Inches(2.8), "MODEL ARCHITECTURE")
    
    tf = add_textbox(slide, Inches(0.85), top + Inches(0.55), half_w - Inches(0.40), half_h - Inches(0.70))
    
    specs = [
        ("Input Tensor:", "1 x 1250 standardized BVP pulse samples (10-second window at 125 Hz) with demographic metadata."),
        ("Multi-Scale 1D-ResNet:", "Dual branches: Kernel=5 (systolic peaks) and Kernel=11 dilated (global waveform rhythms)."),
        ("Temporal Modeling:", "2-layer Bidirectional GRU (hidden=64) capturing cardiac phase periodicity across heartbeats."),
        ("Self-Attention:", "4-head temporal attention weighting high-SNR cardiac cycles over motion-affected cycles."),
        ("Decoupled Heads:", "Separate dense output heads for SBP (stroke volume) and DBP (peripheral resistance).")
    ]
    
    for j, (label, desc) in enumerate(specs):
        add_rich_bullet(tf, label, desc, is_first=(j==0), label_color=TEAL_DEEP, space_after=Pt(9))
    
    # Right side: top = architecture diagram, bottom = demo card
    right_left = Inches(0.65) + half_w + gap
    diagram_h = Inches(3.40)
    
    # Architecture diagram card
    add_card(slide, right_left, top, half_w, diagram_h)
    img_path = os.path.join(ASSETS, "fig_model06_architecture.png")
    add_image_fit(slide, img_path, right_left + Inches(0.15), top + Inches(0.10), half_w - Inches(0.30), diagram_h - Inches(0.20))
    
    # Live Demo Touchpoint card
    demo_top = top + diagram_h + Inches(0.12)
    demo_h = half_h - diagram_h - Inches(0.12)
    
    demo_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_left, demo_top, half_w, demo_h)
    demo_card.fill.solid()
    demo_card.fill.fore_color.rgb = GOLD_PALE
    demo_card.line.color.rgb = GOLD_LIGHT
    demo_card.line.width = Pt(1.5)
    
    # Shadow on demo card
    spPr_demo = demo_card._element.find(qn('p:spPr'))
    shadow_demo = parse_xml(
        f'<a:effectLst {nsdecls("a")}>'
        f'  <a:outerShdw blurRad="50000" dist="25000" dir="5400000" rotWithShape="0">'
        f'    <a:srgbClr val="B8860B"><a:alpha val="12000"/></a:srgbClr>'
        f'  </a:outerShdw>'
        f'</a:effectLst>'
    )
    spPr_demo.append(shadow_demo)
    
    tf_demo = add_textbox(slide, right_left + Inches(0.22), demo_top + Inches(0.15), half_w - Inches(0.44), demo_h - Inches(0.30))
    set_para(tf_demo, "LIVE DEMONSTRATION", font_size=Pt(9), bold=True, color=GOLD, font_name=FONT_HEADING, space_after=Pt(3))
    set_para(tf_demo, "Switching to smartphone for live prototype demo", font_size=Pt(12), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, is_first=False, space_after=Pt(4))
    set_para(tf_demo, "Demonstrating real-time Camera2 video ingestion, forehead ROI tracking, Savitzky-Golay signal smoothing, and on-device blood pressure inference.", font_size=Pt(9), color=TEXT_BODY, is_first=False, space_after=Pt(0))
    
    return slide


def slide_10_results(prs):
    """SLIDE 10: Expected Outcomes & Results (KPI metrics + chart)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 11", "Expected Outcomes & Results", 10)
    
    half_w = Inches(5.87)
    half_h = Inches(5.15)
    gap = Inches(0.20)
    top = Inches(1.55)
    
    # Left side: 4 KPI metric cards stacked
    kpi_w = half_w
    kpi_h = Inches(1.22)
    kpi_gap = Inches(0.12)
    
    kpis = [
        ("10.12 / 5.91", "mmHg", "Exploratory Subject MAE", "Subject-level test error (SBP / DBP) on synchronized evaluation partitions.", TEAL_DEEP),
        ("6.70", "mmHg gain", "Model Progression", "SBP MAE improved by 6.70 mmHg over baseline (MODEL-01: 16.82 to MODEL-06: 10.12).", TEAL_MID),
        ("8.9 dB", "SNR", "POS Chrominance Projection", "Orthogonal skin-plane projection placing specular reflection in the null space.", GOLD),
        ("~120 ms", "latency", "Edge Mobile Execution", "Zero dropped frames with asynchronous offline batching on Android CPU.", TEAL_LIGHT)
    ]
    
    for i, (val, unit, label, desc, accent) in enumerate(kpis):
        kpi_top = top + i * (kpi_h + kpi_gap)
        add_card(slide, Inches(0.65), kpi_top, kpi_w, kpi_h)
        
        # Left accent
        ab = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.65), kpi_top, Inches(0.06), kpi_h)
        ab.fill.solid()
        ab.fill.fore_color.rgb = accent
        ab.line.fill.background()
        
        # Big number
        tf_val = add_textbox(slide, Inches(0.85), kpi_top + Inches(0.12), Inches(2.0), Inches(0.50))
        p_v = tf_val.paragraphs[0]
        r_v = p_v.add_run()
        r_v.text = val
        r_v.font.name = FONT_HEADING
        r_v.font.size = Pt(16)
        r_v.font.bold = True
        r_v.font.color.rgb = accent
        r_u = p_v.add_run()
        r_u.text = f"  {unit}"
        r_u.font.name = FONT_BODY
        r_u.font.size = Pt(10)
        r_u.font.color.rgb = TEXT_SECONDARY
        
        # Label + desc
        tf_ld = add_textbox(slide, Inches(0.85), kpi_top + Inches(0.58), kpi_w - Inches(0.40), Inches(0.55))
        set_para(tf_ld, label, font_size=Pt(10), bold=True, color=TEXT_DARK, font_name=FONT_HEADING, space_after=Pt(2))
        set_para(tf_ld, desc, font_size=Pt(8.5), color=TEXT_SECONDARY, is_first=False, space_after=Pt(0))
    
    # Right card: Chart
    right_left = Inches(0.65) + half_w + gap
    add_card(slide, right_left, top, half_w, half_h)
    add_teal_pill(slide, right_left + Inches(0.18), top + Inches(0.15), Inches(2.8), "BENCHMARK COMPARISON")
    
    img_path = os.path.join(ASSETS, "fig_extractor_benchmark_chart.png")
    add_image_fit(slide, img_path, right_left + Inches(0.20), top + Inches(0.55), half_w - Inches(0.40), half_h - Inches(1.10))
    
    tf_cap = add_textbox(slide, right_left + Inches(0.20), top + half_h - Inches(0.50), half_w - Inches(0.40), Inches(0.40))
    set_para(tf_cap, "rPPG extractor SNR and model error (MAE) benchmark comparison", font_size=Pt(8.5), color=TEXT_SECONDARY, align=PP_ALIGN.CENTER, italic=True, space_after=Pt(0))
    
    return slide


def slide_11_conclusion(prs):
    """SLIDE 11: Conclusion & Future Scope + Thank You."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_canvas_bg(slide)
    build_header_area(slide, "SLIDE 12", "Conclusion Remarks & Future Scope of Work", 11)
    
    half_w = Inches(5.87)
    col_h = Inches(3.55)
    gap = Inches(0.20)
    top = Inches(1.55)
    
    # Left card: Conclusions
    add_card(slide, Inches(0.65), top, half_w, col_h, border_color=BORDER_TEAL)
    add_teal_pill(slide, Inches(0.85), top + Inches(0.15), Inches(2.2), "CONCLUDING REMARKS")
    
    tf_c = add_textbox(slide, Inches(0.85), top + Inches(0.55), half_w - Inches(0.40), col_h - Inches(0.70))
    conclusions = [
        ("Comprehensive Foundation:", "The 6-week training at IIIT-NR provided a strong, multi-faceted grounding across 45 AI topics under expert mentorship."),
        ("Interdisciplinary Application:", "We applied digital signal filtering (Savitzky-Golay) and deep sequence models (CNN-BiGRU-Attention) to optical pulse waveforms."),
        ("Feasibility Demonstrated:", "Exploratory results confirm that standard smartphone cameras can capture meaningful cardiovascular signals."),
        ("Privacy by Design:", "On-device edge inference ensures that no sensitive biometric video data leaves the user's phone.")
    ]
    for j, (label, desc) in enumerate(conclusions):
        add_rich_bullet(tf_c, label, desc, is_first=(j==0), space_after=Pt(8))
    
    # Right card: Future Scope
    right_left = Inches(0.65) + half_w + gap
    add_card(slide, right_left, top, half_w, col_h, border_color=RGBColor(218, 175, 71))
    add_gold_pill(slide, right_left + Inches(0.18), top + Inches(0.15), Inches(2.2), "FUTURE SCOPE")
    
    tf_f = add_textbox(slide, right_left + Inches(0.22), top + Inches(0.55), half_w - Inches(0.44), col_h - Inches(0.70))
    future = [
        ("Diverse Demographics:", "Evaluate across varied skin tones (Fitzpatrick I to VI) and ambient lighting conditions."),
        ("NPU Acceleration:", "Integrate Android NNAPI and INT8 quantization for sub-50ms real-time continuous inference."),
        ("Multi-Modal Sensing:", "Combine front-camera facial rPPG with rear-camera fingertip PPG for optical Pulse Transit Time."),
        ("Clinical Deployment:", "Deploy edge inference on smart mirrors and digital healthcare kiosks for community screening.")
    ]
    for j, (label, desc) in enumerate(future):
        add_rich_bullet(tf_f, label, desc, is_first=(j==0), label_color=GOLD, space_after=Pt(8))
    
    # Bottom gratitude banner (full-width teal card)
    thanks_top = top + col_h + Inches(0.15)
    thanks_h = Inches(1.20)
    
    thanks_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), thanks_top, Inches(11.93), thanks_h)
    thanks_card.fill.solid()
    thanks_card.fill.fore_color.rgb = TEAL_WASH
    thanks_card.line.color.rgb = BORDER_TEAL
    thanks_card.line.width = Pt(1)
    
    tf_thanks = add_textbox(slide, Inches(0.85), thanks_top + Inches(0.12), Inches(11.53), thanks_h - Inches(0.24))
    set_para(tf_thanks, "Heartfelt gratitude to Dr. Anurag Singh (IIIT-NR), Prof. Aparna Pandey (BIT Raipur),\nall faculty members, and the evaluation committee for their invaluable guidance.", font_size=Pt(11), bold=True, color=TEAL_DEEP, font_name=FONT_HEADING, align=PP_ALIGN.CENTER, space_after=Pt(6))
    set_para(tf_thanks, "Thank You  \u2022  Open for Questions & Feedback", font_size=Pt(12), bold=True, color=GOLD, font_name=FONT_HEADING, align=PP_ALIGN.CENTER, is_first=False, space_after=Pt(0))
    
    return slide


# ============================================================================
# MAIN
# ============================================================================

def build():
    print("=" * 60)
    print("BUILDING SCHOLARLY ELEGANCE ACADEMIC DECK")
    print("=" * 60)
    
    prs = create_prs()
    
    builders = [
        ("Slide 1:  Title & Institutional Acknowledgement", slide_01_title),
        ("Slide 2:  Introduction about the Training", slide_02_introduction),
        ("Slide 3:  Training Objectives", slide_03_objectives),
        ("Slide 4:  Training Modules / Topics Covered", slide_04_curriculum),
        ("Slide 5:  Key Learnings", slide_05_key_learnings),
        ("Slide 6:  Proposed Project Title & Introduction", slide_06_project_intro),
        ("Slide 7:  Objectives of the Proposed Project", slide_07_objectives_project),
        ("Slide 8:  Methodology / Approach", slide_08_methodology),
        ("Slide 9:  Work Details & Live Demo Touchpoint", slide_09_work_details_demo),
        ("Slide 10: Expected Outcomes & Results", slide_10_results),
        ("Slide 11: Conclusion & Future Scope", slide_11_conclusion),
    ]
    
    for label, builder in builders:
        print(f"  Building {label}...")
        builder(prs)
    
    for path in [OUT_PRIMARY, OUT_ACADEMIC, OUT_DOWNLOADS]:
        prs.save(path)
        print(f"  Saved: {path}")
    
    print("=" * 60)
    print("ALL 11 SLIDES COMPILED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    build()
