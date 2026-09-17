r"""
generate_dark_tech_deck.py

Modular, Senior-Grade python-pptx Architecture for 'Modern Dark Mode Tech' Presentations.
Implements the exact design system:
  - Dark Charcoal Solid Background (RGB: 15, 20, 30)
  - Pure White Primary Text (RGB: 255, 255, 255)
  - Light Gray Secondary / Body Text (RGB: 200, 200, 200)
  - Vibrant Teal Accents (RGB: 0, 180, 200)
  - Warm Amber Section & Callout Accents (RGB: 245, 158, 11)

Outputs:
  1. technical_presentation_draft.pptx  (Clean template & modular example deck)
  2. VT_2026_rPPG_to_BP_Estimation.pptx (Full 11-slide Capstone & VT presentation)
  3. C:\Users\simpl\Downloads\Sample PPT _VT 2026.pptx (Updated template file)
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# =============================================================================
# 1. DESIGN SYSTEM CONSTANTS & COLOR PALETTE
# =============================================================================
COLOR_BG_DARK       = RGBColor(15, 20, 30)     # #0F141E - Dark Charcoal
COLOR_CARD_BG       = RGBColor(24, 32, 47)     # #18202F - Dark Card Fill
COLOR_CARD_BORDER   = RGBColor(40, 52, 75)     # #28344B - Subtle Card Border
COLOR_TEXT_WHITE    = RGBColor(255, 255, 255) # #FFFFFF - Pure White
COLOR_TEXT_MUTED    = RGBColor(200, 200, 200) # #C8C8C8 - Light Gray
COLOR_TEXT_DIM      = RGBColor(148, 163, 184) # #94A3B8 - Slate Dim Gray
COLOR_TEAL_ACCENT   = RGBColor(0, 180, 200)   # #00B4C8 - Vibrant Teal
COLOR_AMBER_ACCENT  = RGBColor(245, 158, 11)  # #F59E0B - Warm Amber
COLOR_EMERALD       = RGBColor(16, 185, 129)  # #10B981 - Emerald Green

FONT_PRIMARY = "Arial"
FONT_BODY    = "Calibri"

SLIDE_WIDTH_INCHES  = 13.333
SLIDE_HEIGHT_INCHES = 7.500

WORKSPACE_DIR = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation"
ASSETS_DIR    = os.path.join(WORKSPACE_DIR, "presentation", "assets")
DRAFT_OUTPUT  = os.path.join(WORKSPACE_DIR, "presentation", "technical_presentation_draft.pptx")
FULL_OUTPUT   = os.path.join(WORKSPACE_DIR, "presentation", "VT_2026_rPPG_to_BP_Estimation.pptx")
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

def apply_dark_background(slide):
    """Fills the slide background with Dark Charcoal (RGB: 15, 20, 30)."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG_DARK

def add_header_banner(slide, title, category=None):
    """
    Standard top header for content slides:
      - Category badge (Vibrant Teal / Warm Amber)
      - Pure White title
      - 2-point Vibrant Teal accent line underneath
    """
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.73), Inches(0.95))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    if category:
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = FONT_PRIMARY
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_TEAL_ACCENT
        p_cat.space_after = Pt(2)
        p_title = tf.add_paragraph()
    else:
        p_title = tf.paragraphs[0]

    p_title.text = title
    p_title.font.name = FONT_PRIMARY
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_WHITE
    p_title.alignment = PP_ALIGN.LEFT

    # 2-point horizontal Teal accent line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.73), Pt(2))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_TEAL_ACCENT
    line.line.color.rgb = COLOR_TEAL_ACCENT
    line.line.width = Pt(0)

def add_card_box(slide, left, top, width, height, fill_color=COLOR_CARD_BG, border_color=COLOR_CARD_BORDER, border_width=Pt(1)):
    """Draws a modern rounded dark card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = fill_color
    card.line.color.rgb = border_color
    card.line.width = border_width
    return card

# =============================================================================
# 3. MODULAR SLIDE LAYOUT FUNCTIONS
# =============================================================================

def add_title_slide(prs, title, subtitle, presenters=None, department=None, institution=None, kpis=None):
    """
    add_title_slide:
      Centered text. Draws a 2-point thickness Teal accent line horizontally
      between the title and subtitle. Supports optional presenter credentials and KPI pills.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)

    # Top Tag Badge
    badge_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.33), Inches(0.4))
    btf = badge_box.text_frame
    btf.word_wrap = True
    bp = btf.paragraphs[0]
    bp.text = "RESEARCH & TECHNICAL PRESENTATION"
    bp.font.name = FONT_PRIMARY
    bp.font.size = Pt(11)
    bp.font.bold = True
    bp.font.color.rgb = COLOR_TEAL_ACCENT
    bp.alignment = PP_ALIGN.CENTER

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.25), Inches(11.33), Inches(1.6))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    tp = ttf.paragraphs[0]
    tp.text = title
    tp.font.name = FONT_PRIMARY
    tp.font.size = Pt(30)
    tp.font.bold = True
    tp.font.color.rgb = COLOR_TEXT_WHITE
    tp.alignment = PP_ALIGN.CENTER

    # 2-Point Vibrant Teal Horizontal Accent Line
    line_w = Inches(5.0)
    line_left = (Inches(SLIDE_WIDTH_INCHES) - line_w) / 2
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, line_left, Inches(2.95), line_w, Pt(2))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_TEAL_ACCENT
    line.line.color.rgb = COLOR_TEAL_ACCENT
    line.line.width = Pt(0)

    # Subtitle Box
    sub_box = slide.shapes.add_textbox(Inches(1.0), Inches(3.15), Inches(11.33), Inches(0.8))
    stf = sub_box.text_frame
    stf.word_wrap = True
    sp = stf.paragraphs[0]
    sp.text = subtitle
    sp.font.name = FONT_BODY
    sp.font.size = Pt(16)
    sp.font.color.rgb = COLOR_TEXT_MUTED
    sp.alignment = PP_ALIGN.CENTER

    # Presenters & Metadata Box
    if presenters or department or institution:
        meta_box = slide.shapes.add_textbox(Inches(1.0), Inches(3.95), Inches(11.33), Inches(1.4))
        mtf = meta_box.text_frame
        mtf.word_wrap = True
        
        if presenters:
            p_pres = mtf.paragraphs[0]
            p_pres.text = "Presented By: " + " • ".join(presenters)
            p_pres.font.name = FONT_PRIMARY
            p_pres.font.size = Pt(13)
            p_pres.font.bold = True
            p_pres.font.color.rgb = COLOR_TEXT_WHITE
            p_pres.alignment = PP_ALIGN.CENTER
            p_pres.space_after = Pt(4)
        
        if department or institution:
            p_dept = mtf.add_paragraph() if presenters else mtf.paragraphs[0]
            parts = [p for p in [department, institution] if p]
            p_dept.text = " • ".join(parts)
            p_dept.font.name = FONT_BODY
            p_dept.font.size = Pt(13)
            p_dept.font.color.rgb = COLOR_AMBER_ACCENT
            p_dept.alignment = PP_ALIGN.CENTER

    # Optional 3 Glass KPI Cards at Bottom
    if kpis and len(kpis) >= 3:
        card_w = Inches(3.64)
        card_gap = Inches(0.4)
        card_top = Inches(5.45)
        card_h = Inches(1.5)
        
        for i, (val, unit, label, desc) in enumerate(kpis[:3]):
            c_left = Inches(1.0) + i * (card_w + card_gap)
            add_card_box(slide, c_left, card_top, card_w, card_h, fill_color=COLOR_CARD_BG, border_color=COLOR_TEAL_ACCENT if i==0 else COLOR_CARD_BORDER)
            
            tb = slide.shapes.add_textbox(c_left + Inches(0.15), card_top + Inches(0.1), card_w - Inches(0.3), card_h - Inches(0.2))
            tf = tb.text_frame
            tf.word_wrap = True
            
            p1 = tf.paragraphs[0]
            p1.text = f"{val} "
            p1.font.name = FONT_PRIMARY
            p1.font.size = Pt(18)
            p1.font.bold = True
            p1.font.color.rgb = COLOR_TEAL_ACCENT if i==0 else (COLOR_AMBER_ACCENT if i==1 else COLOR_EMERALD)
            r_u = p1.add_run()
            r_u.text = unit
            r_u.font.size = Pt(11)
            r_u.font.color.rgb = COLOR_TEXT_DIM
            p1.space_after = Pt(2)
            
            p2 = tf.add_paragraph()
            p2.text = label
            p2.font.name = FONT_PRIMARY
            p2.font.size = Pt(11)
            p2.font.bold = True
            p2.font.color.rgb = COLOR_TEXT_WHITE
            
            p3 = tf.add_paragraph()
            p3.text = desc
            p3.font.name = FONT_BODY
            p3.font.size = Pt(9.5)
            p3.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def add_section_header(prs, heading, subheading=None):
    """
    add_section_header:
      Left-aligned, massive typography, with a vertical Warm Amber accent block
      on the far left margin.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)

    # Vertical Warm Amber Accent Block on far left
    amber_block = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.7), Inches(0.18), Inches(2.2))
    amber_block.fill.solid()
    amber_block.fill.fore_color.rgb = COLOR_AMBER_ACCENT
    amber_block.line.color.rgb = COLOR_AMBER_ACCENT
    amber_block.line.width = Pt(0)

    # Massive Section Heading Box
    head_box = slide.shapes.add_textbox(Inches(1.2), Inches(2.6), Inches(11.0), Inches(2.4))
    htf = head_box.text_frame
    htf.word_wrap = True
    
    p_tag = htf.paragraphs[0]
    p_tag.text = "SECTION BREAK"
    p_tag.font.name = FONT_PRIMARY
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_AMBER_ACCENT
    p_tag.space_after = Pt(6)

    p_head = htf.add_paragraph()
    p_head.text = heading
    p_head.font.name = FONT_PRIMARY
    p_head.font.size = Pt(36)
    p_head.font.bold = True
    p_head.font.color.rgb = COLOR_TEXT_WHITE
    
    if subheading:
        p_head.space_after = Pt(8)
        p_sub = htf.add_paragraph()
        p_sub.text = subheading
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(16)
        p_sub.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def add_content_slide(prs, title, bullet_points, category=None):
    """
    add_content_slide:
      Standard layout with generous margins (pptx.util.Inches) and styled cards.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)
    add_header_banner(slide, title, category)

    # Large Content Card Container
    add_card_box(slide, Inches(0.8), Inches(1.6), Inches(11.73), Inches(5.3))

    # Content Text Box with generous padding
    tb = slide.shapes.add_textbox(Inches(1.1), Inches(1.85), Inches(11.13), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    for i, bullet in enumerate(bullet_points):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        
        if isinstance(bullet, tuple):
            prefix, text = bullet
            p.text = f"• {prefix}: "
            p.font.name = FONT_PRIMARY
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = COLOR_TEXT_WHITE
            
            run = p.add_run()
            run.text = text
            run.font.name = FONT_BODY
            run.font.bold = False
            run.font.color.rgb = COLOR_TEXT_MUTED
        else:
            p.text = f"• {bullet}"
            p.font.name = FONT_BODY
            p.font.size = Pt(14)
            p.font.color.rgb = COLOR_TEXT_MUTED

        p.space_after = Pt(12)

    return slide

def add_split_slide(prs, title, left_bullets, right_image_placeholder_text="[ Insert Graph / Architecture Diagram Here ]", right_image_path=None, category=None):
    """
    add_split_slide:
      Two-column layout.
      Left side: holds bullet points in a dark card container.
      Right side: subtle dark gray rectangle with a teal outline acting as a placeholder
      or embedding the real image if provided.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)
    add_header_banner(slide, title, category)

    col_w_left  = Inches(5.2)
    col_w_right = Inches(6.23)
    col_h       = Inches(5.3)
    top_pos     = Inches(1.6)

    # Left Column Container
    add_card_box(slide, Inches(0.8), top_pos, col_w_left, col_h)
    tb_left = slide.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.2), col_w_left - Inches(0.4), col_h - Inches(0.4))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    for i, bullet in enumerate(left_bullets):
        p = tf_l.paragraphs[0] if i == 0 else tf_l.add_paragraph()
        if isinstance(bullet, tuple):
            prefix, text = bullet
            p.text = f"• {prefix}: "
            p.font.name = FONT_PRIMARY
            p.font.size = Pt(12.5)
            p.font.bold = True
            p.font.color.rgb = COLOR_TEXT_WHITE
            
            run = p.add_run()
            run.text = text
            run.font.name = FONT_BODY
            run.font.bold = False
            run.font.color.rgb = COLOR_TEXT_MUTED
        else:
            p.text = f"• {bullet}"
            p.font.name = FONT_BODY
            p.font.size = Pt(12.5)
            p.font.color.rgb = COLOR_TEXT_MUTED

        p.space_after = Pt(8)

    # Right Column: Placeholder Rectangle with Vibrant Teal Outline OR Real Image
    right_left = Inches(0.8) + col_w_left + Inches(0.3)

    if right_image_path and os.path.exists(right_image_path):
        # Embed Image inside a clean dark container
        add_card_box(slide, right_left, top_pos, col_w_right, col_h, border_color=COLOR_TEAL_ACCENT, border_width=Pt(1.5))
        # Insert image slightly inset
        slide.shapes.add_picture(right_image_path, right_left + Inches(0.1), top_pos + Inches(0.1), col_w_right - Inches(0.2), col_h - Inches(0.5))
        # Caption below image
        tb_cap = slide.shapes.add_textbox(right_left, top_pos + col_h - Inches(0.35), col_w_right, Inches(0.3))
        tf_c = tb_cap.text_frame
        p_c = tf_c.paragraphs[0]
        p_c.text = right_image_placeholder_text
        p_c.font.name = FONT_BODY
        p_c.font.size = Pt(9.5)
        p_c.font.color.rgb = COLOR_TEXT_DIM
        p_c.alignment = PP_ALIGN.CENTER
    else:
        # Subtle Dark Gray placeholder rectangle with Vibrant Teal Outline
        ph_box = add_card_box(slide, right_left, top_pos, col_w_right, col_h, fill_color=COLOR_CARD_BG, border_color=COLOR_TEAL_ACCENT, border_width=Pt(1.5))
        
        tb_ph = slide.shapes.add_textbox(right_left + Inches(0.3), top_pos + Inches(1.8), col_w_right - Inches(0.6), Inches(1.5))
        tf_p = tb_ph.text_frame
        tf_p.word_wrap = True
        p_icon = tf_p.paragraphs[0]
        p_icon.text = "📈 [ DATA VISUALIZATION / ARCHITECTURE ]"
        p_icon.font.name = FONT_PRIMARY
        p_icon.font.size = Pt(13)
        p_icon.font.bold = True
        p_icon.font.color.rgb = COLOR_TEAL_ACCENT
        p_icon.alignment = PP_ALIGN.CENTER
        p_icon.space_after = Pt(6)

        p_desc = tf_p.add_paragraph()
        p_desc.text = right_image_placeholder_text
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_TEXT_MUTED
        p_desc.alignment = PP_ALIGN.CENTER

    return slide

def add_card_grid_slide(prs, title, cards_data, columns=3, category=None):
    """
    add_card_grid_slide:
      Generates a responsive multi-card dark tech grid (2 or 3 columns).
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)
    add_header_banner(slide, title, category)

    num_cards = len(cards_data)
    rows = (num_cards + columns - 1) // columns
    
    total_w = Inches(11.73)
    gap_x   = Inches(0.25)
    gap_y   = Inches(0.2)
    card_w  = (total_w - (columns - 1) * gap_x) / columns
    
    total_h = Inches(5.3)
    card_h  = (total_h - (rows - 1) * gap_y) / rows
    top_base = Inches(1.6)

    for i, card in enumerate(cards_data):
        r = i // columns
        c = i % columns
        c_left = Inches(0.8) + c * (card_w + gap_x)
        c_top  = top_base + r * (card_h + gap_y)

        accent_border = COLOR_TEAL_ACCENT if i % 2 == 0 else COLOR_CARD_BORDER
        add_card_box(slide, c_left, c_top, card_w, card_h, border_color=accent_border)

        tb = slide.shapes.add_textbox(c_left + Inches(0.12), c_top + Inches(0.1), card_w - Inches(0.24), card_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = card.get('title', f'Card {i+1}')
        p1.font.name = FONT_PRIMARY
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_TEXT_WHITE
        p1.space_after = Pt(4)

        if 'tag' in card:
            # Add small badge
            p1.text = f"{card['tag']} • {card['title']}"
            p1.font.color.rgb = COLOR_TEAL_ACCENT

        if 'items' in card:
            for item in card['items']:
                pi = tf.add_paragraph()
                pi.text = f"• {item}"
                pi.font.name = FONT_BODY
                pi.font.size = Pt(10.5)
                pi.font.color.rgb = COLOR_TEXT_MUTED
                pi.space_after = Pt(2)
        elif 'desc' in card:
            p2 = tf.add_paragraph()
            p2.text = card['desc']
            p2.font.name = FONT_BODY
            p2.font.size = Pt(11)
            p2.font.color.rgb = COLOR_TEXT_MUTED

    return slide

def add_table_slide(prs, title, headers, rows_data, highlight_last=True, metrics_list=None, category=None):
    """
    add_table_slide:
      Generates a dark-themed benchmark data table with optional metrics box.
    """
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_background(slide)
    add_header_banner(slide, title, category)

    has_metrics = bool(metrics_list)
    tbl_w = Inches(11.73) if not has_metrics else Inches(6.0)
    tbl_h = Inches(4.8)
    top_pos = Inches(1.6)

    # Add Table Shape
    num_rows = len(rows_data) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(num_rows, num_cols, Inches(0.8), top_pos, tbl_w, tbl_h)
    tbl = table_shape.table

    # Style Header Row
    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59) # Deep Slate Header
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL_ACCENT
        p.alignment = PP_ALIGN.CENTER

    # Style Data Rows
    for row_idx, r_vals in enumerate(rows_data, 1):
        is_hl = (row_idx == len(rows_data)) and highlight_last
        for col_idx, val in enumerate(r_vals):
            cell = tbl.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(24, 38, 64) if is_hl else (COLOR_CARD_BG if row_idx % 2 == 1 else RGBColor(18, 24, 36))
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_PRIMARY if is_hl else FONT_BODY
            p.font.size = Pt(10.5)
            p.font.bold = is_hl
            p.font.color.rgb = COLOR_TEXT_WHITE if is_hl else COLOR_TEXT_MUTED
            p.alignment = PP_ALIGN.CENTER if col_idx > 0 else PP_ALIGN.LEFT

    # Metrics Box on Right Side
    if has_metrics:
        m_left = Inches(0.8) + tbl_w + Inches(0.33)
        m_w    = Inches(11.73) - tbl_w - Inches(0.33)
        add_card_box(slide, m_left, top_pos, m_w, tbl_h, border_color=COLOR_TEAL_ACCENT)
        
        tb = slide.shapes.add_textbox(m_left + Inches(0.2), top_pos + Inches(0.2), m_w - Inches(0.4), tbl_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = "Key Validated Metrics"
        p.font.name = FONT_PRIMARY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEAL_ACCENT
        p.space_after = Pt(8)

        for m_title, m_desc in metrics_list:
            pm = tf.add_paragraph()
            pm.text = f"• {m_title}: "
            pm.font.name = FONT_PRIMARY
            pm.font.size = Pt(11.5)
            pm.font.bold = True
            pm.font.color.rgb = COLOR_TEXT_WHITE
            
            run = pm.add_run()
            run.text = m_desc
            run.font.name = FONT_BODY
            run.font.bold = False
            run.font.color.rgb = COLOR_TEXT_MUTED
            pm.space_after = Pt(6)

    return slide

# =============================================================================
# 4. BUILDING DRAFT PRESENTATION (technical_presentation_draft.pptx)
# =============================================================================

def build_draft_presentation():
    """Builds a clean demonstration draft presentation demonstrating all modular functions."""
    print(f"Generating draft presentation: {DRAFT_OUTPUT}")
    prs = create_presentation()

    # 1. Title Slide
    add_title_slide(
        prs,
        title="Mobile Remote Photoplethysmography to\nCuffless Blood Pressure Estimation",
        subtitle="Modern Dark Mode Tech Design System & Modular Python Architecture",
        presenters=["Vedang Bhatt", "Anubhav Shrivastav", "Aadarsh"],
        department="Department of Computer Science & Engineering",
        institution="Bhilai Institute of Technology, Raipur",
        kpis=[
            ("10.12 / 5.91", "mmHg", "Subject-Level Accuracy", "Evaluated on synchronized clinical benchmark."),
            ("120", "ms", "Edge Latency", "Offline single-shot TFLite batch inference."),
            ("100%", "On-Device", "Privacy-Preserving", "Zero cloud dependency on commodity Android.")
        ]
    )

    # 2. Section Header
    add_section_header(
        prs,
        heading="Stage 1: Optical Frontend & Physiological DSP",
        subheading="Eliminating sensor gain jitter and isolating microvascular blood volume pulse"
    )

    # 3. Content Slide
    add_content_slide(
        prs,
        title="Photometric Convergence & Facial ROI Tracking",
        category="Optical Engineering",
        bullet_points=[
            ("Camera2 AE/AWB Finite State Machine", "Pulsatile hemoglobin absorption is only 0.1%–1.5% of skin reflectance. A 3-phase state machine (Convergence, Hold, Lock) locks ISO and exposure time before acquisition."),
            ("468-Point MediaPipe Face Mesh", "Dynamically tracks the anatomical forehead region, providing high capillary perfusion and eliminating motion artifacts."),
            ("PCHIP Resampling (125 Hz)", "Standardizes variable 28–38 ms camera timestamps onto a strict 125 Hz uniform grid without Runge overshoot."),
            ("Specular Noise Rejection", "Plane-Orthogonal-to-Skin (POS) projection algebraically cancels specular white reflections, achieving 8.9 dB SNR.")
        ]
    )

    # 4. Split Slide (With Image Placeholder)
    add_split_slide(
        prs,
        title="End-to-End Deep Pipeline Architecture",
        category="System Architecture",
        left_bullets=[
            ("Photometric Lock", "Hardware locks exposure & ISO gain to eliminate sensor jitter."),
            ("Forehead ROI", "Extracts spatial RGB mean across tracked forehead capillary beds."),
            ("Dual-Stream DSP", "Butterworth bandpass [0.75, 3.0 Hz] + BayesShrink sym8 Wavelet denoising."),
            ("Neural Inference", "MODEL-06-SepHead predicts continuous SBP/DBP in 120 ms.")
        ],
        right_image_placeholder_text="Figure 1: End-to-End Acquisition & Inference Flow",
        right_image_path=os.path.join(ASSETS_DIR, "fig_pipeline_overview.png")
    )

    # 5. Table Slide
    add_table_slide(
        prs,
        title="Empirical Model Progression & Benchmarks",
        category="Experimental Results",
        headers=["Model Generation", "SBP MAE", "DBP MAE", "Subject SBP/DBP"],
        rows_data=[
            ["MODEL-01 (Demo MLP)", "16.82 mmHg", "9.41 mmHg", "15.90 / 8.85 mmHg"],
            ["MODEL-03 (1D-ResNet)", "14.20 mmHg", "8.12 mmHg", "13.10 / 7.40 mmHg"],
            ["MODEL-05 (+BiGRU+MHSA)", "12.65 mmHg", "7.20 mmHg", "11.45 / 6.55 mmHg"],
            ["MODEL-06-SepHead (Ours)", "11.58 mmHg", "6.70 mmHg", "10.12 / 5.91 mmHg"]
        ],
        highlight_last=True,
        metrics_list=[
            ("Subject-Level Accuracy", "10.12 mmHg SBP | 5.91 mmHg DBP MAE on MCD-Iriun dataset."),
            ("Progression Delta", "6.70 mmHg SBP MAE improvement over baseline."),
            ("Extractor Benchmarks", "POS achieves 8.9 dB SNR; TS-CAN achieves 10.4 dB SNR."),
            ("Mobile Runtime", "120 ms batch inference on mobile CPU with zero frame drops.")
        ]
    )

    prs.save(DRAFT_OUTPUT)
    print(f"Draft saved successfully to: {DRAFT_OUTPUT}")

# =============================================================================
# 5. BUILDING FULL 11-SLIDE VT CAPSTONE PRESENTATION
# =============================================================================

def build_full_vt_presentation():
    """Generates the full 11-slide presentation matching the VT 2026 format in Dark Mode Tech theme."""
    print(f"Generating full VT presentation: {FULL_OUTPUT}")
    prs = create_presentation()

    # Presenters & Institution
    presenters = ["1. Vedang Bhatt", "2. Anubhav Shrivastav", "3. Aadarsh"]
    dept = "Department of Computer Science & Engineering"
    inst = "Bhilai Institute of Technology, Raipur"

    # -------------------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------------------
    add_title_slide(
        prs,
        title="Mobile Remote Photoplethysmography to\nCuffless Blood Pressure Estimation",
        subtitle="A Presentation on Vocational Training & Proposed Project (01/06/2026 to 15/07/2026)",
        presenters=presenters,
        department=dept,
        institution=inst,
        kpis=[
            ("10.12 / 5.91", "mmHg", "Subject Accuracy", "MCD-Iriun Synchronized Dataset"),
            ("120", "ms", "Edge Execution", "Zero frame drops on mobile CPU"),
            ("100%", "On-Device", "Privacy Native", "Single-point personal calibration")
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 2: Slide 2: Introduction about the training undergone
    # -------------------------------------------------------------------------
    add_card_grid_slide(
        prs,
        title="Slide 2: Introduction about the Training Undergone",
        category="Vocational Training Overview",
        columns=3,
        cards_data=[
            {
                "tag": "01",
                "title": "Domain & Industrial Context",
                "items": [
                    "Focus: Applied Edge AI, Real-time CV & Physiological Computing.",
                    "Shift: Moving from bulky arm cuffs to contactless optical sensing.",
                    "Foundation: Tracking microvascular pulsatile absorption from 30 FPS video."
                ]
            },
            {
                "tag": "02",
                "title": "Core Engineering Scope",
                "items": [
                    "Camera2 API explicit sensor lock (ISO & exposure).",
                    "MediaPipe 468-point 3D landmarking for forehead ROI.",
                    "Optical algorithms: POS, CHROM, and TS-CAN attention.",
                    "PCHIP 125 Hz standardization & Wavelet denoising."
                ]
            },
            {
                "tag": "03",
                "title": "Deep Learning & Edge Delivery",
                "items": [
                    "Multi-scale 1D-ResNet + BiGRU + Self-Attention.",
                    "Decoupled SBP / DBP regression heads.",
                    "Quantized TFLite offline batching on Android.",
                    "ISO 81060-2 clinical compliance benchmarking."
                ]
            }
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 3: Slide 3: Training Objectives
    # -------------------------------------------------------------------------
    add_content_slide(
        prs,
        title="Slide 3: Training Objectives",
        category="Core Technical Milestones",
        bullet_points=[
            ("Objective 1: Transcutaneous Optical Foundations", "Master Beer-Lambert light attenuation, diffuse skin reflectance vs specular white reflection, and POS/CHROM chrominance subspace projection mathematics."),
            ("Objective 2: Real-Time Facial Biometrics", "Deploy 468-point 3D MediaPipe Face Mesh on mobile RGB frames to isolate the forehead microvascular ROI with spatial averaging to suppress CMOS shot noise."),
            ("Objective 3: Physiological Signal Conditioning", "Develop dual-stream DSP pipelines: PCHIP 125 Hz resampling for variable frame rates, 4th-order Butterworth filtering, BayesShrink wavelet denoising, and SQI quality gates."),
            ("Objective 4: Deep Sequence Hemodynamic Modeling", "Implement multi-scale 1D-ResNet with BiGRU and Self-Attention (MODEL-06-SepHead) with decoupled linear heads to map pulsatile morphology to continuous SBP/DBP."),
            ("Objective 5: Mobile Edge Optimization", "Eliminate real-time JNI garbage collection bottlenecks via an asynchronous 'Record-then-Process' state machine and deploy quantized TFLite inference sub-150ms.")
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 4: Slide 4: Training Modules / Topics Covered
    # -------------------------------------------------------------------------
    add_card_grid_slide(
        prs,
        title="Slide 4: Training Modules / Topics Covered",
        category="Detailed Curriculum Breakdown",
        columns=5,
        cards_data=[
            {
                "tag": "MOD 1",
                "title": "Optical Physics",
                "items": [
                    "Beer-Lambert law",
                    "POS null-space math",
                    "CHROM & TS-CAN",
                    "Specular cancellation"
                ]
            },
            {
                "tag": "MOD 2",
                "title": "Vision & Mesh",
                "items": [
                    "Camera2 API YUV->RGB",
                    "MediaPipe 468 landmarks",
                    "Forehead ROI averaging",
                    "EAR blink anti-spoofing"
                ]
            },
            {
                "tag": "MOD 3",
                "title": "Physiological DSP",
                "items": [
                    "PCHIP 125 Hz resampling",
                    "Butterworth bandpass",
                    "BayesShrink sym8 DWT",
                    "SPA detrending & SQI"
                ]
            },
            {
                "tag": "MOD 4",
                "title": "Neural Models",
                "items": [
                    "1D-ResNet multi-scale",
                    "BiGRU recurrence",
                    "4-head Self-Attention",
                    "Decoupled SBP/DBP heads"
                ]
            },
            {
                "tag": "MOD 5",
                "title": "Edge Mobile",
                "items": [
                    "Record-then-Process",
                    "Camera2 AE/AWB lock",
                    "TFLite quantization",
                    "Zero dropped frames"
                ]
            }
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 5: Slide 5: Key Learnings
    # -------------------------------------------------------------------------
    add_card_grid_slide(
        prs,
        title="Slide 5: Key Learnings",
        category="Critical Insights & Discoveries",
        columns=2,
        cards_data=[
            {
                "tag": "PHYSICS",
                "title": "1. The Physics of 'Template Collapse'",
                "desc": "Neural networks trained naively on uncalibrated rPPG regress toward population means (~120/70 mmHg). Root causes: arterial Windkessel low-pass filtering attenuates dicrotic notch by 1-2 orders; 8-bit quantization limits noise floor to 0.39%; 30 FPS limits Nyquist resolution. Solution: Single-point personal calibration."
            },
            {
                "tag": "SIGNAL PROCESSING",
                "title": "2. Derivative Noise Amplification Pitfall",
                "desc": "Ablation tests revealed that multi-channel derivative tensors (vPPG, aPPG) degrade accuracy on real camera data. At 30 FPS with 8-bit quantization, discrete differentiation acts as a high-pass filter that amplifies sensor noise by O(f²). Single-channel raw PPG achieves superior generalization (10.12 vs 14.80 mmHg SBP MAE)."
            },
            {
                "tag": "OPTICS",
                "title": "3. Specular Reflection Algebraic Nulling (POS)",
                "desc": "Pulsatile hemoglobin modulation represents merely 0.1%–1.5% of skin reflectance. By projecting normalized RGB signals orthogonal to the skin-tone reflection plane, the POS algorithm places dominant specular white reflection (R=G=B) directly into the mathematical null space, boosting pulse SNR from 2.4 dB to 8.9 dB."
            },
            {
                "tag": "EDGE ARCHITECTURE",
                "title": "4. Asynchronous Record-then-Process State Machine",
                "desc": "Frame-by-frame JNI calls during real-time 30 FPS camera preview cause Android garbage collection pauses and dropped frames, corrupting temporal signal consistency. Buffering raw spatial RGB data across a 7–10s window and executing single-shot TFLite batch inference offline achieves zero dropped frames and 120 ms latency."
            }
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 6: Slide 6: Proposed Project Title & its Introduction
    # -------------------------------------------------------------------------
    add_split_slide(
        prs,
        title="Slide 6: Proposed Project Title & its Introduction",
        category="Proposed Capstone Project Definition",
        left_bullets=[
            ("Proposed Title", "Mobile Remote Photoplethysmography to Cuffless Blood Pressure Estimation."),
            ("Global Health Burden", "Hypertension affects over 1.28 billion adults globally, serving as the leading risk factor for stroke and cardiovascular disease."),
            ("Conventional Limitations", "Standard occlusive arm cuffs are intermittent, bulky, uncomfortable, and sleep-disruptive during 24-hour ambulatory monitoring."),
            ("White-Coat Hypertension", "In-clinic cuff inflation often triggers transient stress responses, causing misdiagnosis.")
        ],
        right_image_placeholder_text="Contactless Optical Blood Volume Pulse (rPPG) Paradigm",
        right_image_path=os.path.join(ASSETS_DIR, "fig_windkessel_damping.png")
    )

    # -------------------------------------------------------------------------
    # SLIDE 7: Slide 7: Objectives of the Proposed Project
    # -------------------------------------------------------------------------
    add_content_slide(
        prs,
        title="Slide 7: Objectives of the Proposed Project",
        category="System Specifications & Deliverables",
        bullet_points=[
            ("1. Real-Time Microvascular Pulse Extraction", "Capture high-SNR optical blood volume pulse (rPPG) signals from 30 FPS RGB facial video using MediaPipe 468-point forehead tracking and POS null-space projection without any physical contact."),
            ("2. High-Fidelity Physiological DSP Standardization", "Resample variable frame rate video to a strict 125 Hz uniform grid via PCHIP interpolation without Runge oscillations, and apply BayesShrink wavelet denoising to eliminate respiratory baseline wander."),
            ("3. Decoupled Continuous SBP / DBP Neural Estimation", "Train a multi-scale 1D-ResNet + BiGRU + Multi-Head Self-Attention neural architecture (MODEL-06-SepHead) to achieve subject-level accuracy < 11.0 mmHg SBP MAE and < 6.5 mmHg DBP MAE on synchronized clinical datasets."),
            ("4. Single-Point Personal Calibration Integration", "Incorporate a single baseline cuff offset to anchor individual arterial compliance and peripheral vascular tone, overcoming Template Collapse and meeting ISO 81060-2 clinical standards."),
            ("5. Privacy-Preserving 100% On-Device Mobile Execution", "Deploy the full end-to-end acquisition, signal processing, and quantized TFLite inference pipeline on Android devices with an offline latency of ~120 ms and zero cloud data transmission.")
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 8: Slide 9: Methodology / Approach of the Proposed Project
    # -------------------------------------------------------------------------
    add_split_slide(
        prs,
        title="Slide 9: Methodology / Approach of the Proposed Project",
        category="End-to-End Pipeline Architecture",
        left_bullets=[
            ("Stage 0: Photometric Lock", "Camera2 AE/AWB state machine locks ISO gain and exposure duration to eliminate sensor gain oscillations."),
            ("Stage 1: Forehead ROI", "MediaPipe 468 landmarks isolate the central forehead; computes spatial mean across tracked pixels."),
            ("Stage 2: POS Chrominance", "Projects RGB into skin-orthogonal subspace, placing specular reflection in null space (8.9 dB SNR)."),
            ("Stage 3: Physiological DSP", "PCHIP 125 Hz + Butterworth bandpass + BayesShrink DWT denoising + SQI gate."),
            ("Stage 4 & 5: Deep Model", "MODEL-06-SepHead predicts continuous SBP/DBP in 120 ms on Android hardware.")
        ],
        right_image_placeholder_text="Figure 1: End-to-End Pipeline Flow Diagram",
        right_image_path=os.path.join(ASSETS_DIR, "fig_pipeline_overview.png")
    )

    # -------------------------------------------------------------------------
    # SLIDE 9: Slide 10: Proposed Project Work Details
    # -------------------------------------------------------------------------
    add_split_slide(
        prs,
        title="Slide 10: Proposed Project Work Details",
        category="MODEL-06-SepHead Architecture",
        left_bullets=[
            ("Input Tensor", "1 x 1250 standardized BVP samples (10s @ 125 Hz) + 3D demographic metadata."),
            ("Branch 1 (Local Morphology)", "Kernel=5, Stride=2, 3x ResBlock1D (captures systolic upstroke & dicrotic notch)."),
            ("Branch 2 (Global Context)", "Kernel=11, Dilated (1, 2, 2), 3x ResBlock1D (captures rhythm & low frequencies)."),
            ("Sequence Modeling", "2-layer BiGRU (hidden=64) + 4-head Multi-Head Self-Attention for global cycle weighting."),
            ("Decoupled Loss", "L = λ_sbp ||ŷ_sbp - y_sbp||² + λ_dbp ||ŷ_dbp - y_dbp||² to prevent gradient interference.")
        ],
        right_image_placeholder_text="Figure 2: MODEL-06-SepHead Topology & Decoupled Heads",
        right_image_path=os.path.join(ASSETS_DIR, "fig_model06_architecture.png")
    )

    # -------------------------------------------------------------------------
    # SLIDE 10: Slide 11: Expected Outcomes & Results of the Proposed Project Work
    # -------------------------------------------------------------------------
    add_table_slide(
        prs,
        title="Slide 11: Expected Outcomes & Results of the Proposed Project Work",
        category="Empirical Benchmarks & Ablations",
        headers=["Model Generation", "SBP MAE", "DBP MAE", "Subject SBP/DBP"],
        rows_data=[
            ["MODEL-01 (Demo MLP)", "16.82 mmHg", "9.41 mmHg", "15.90 / 8.85 mmHg"],
            ["MODEL-03 (1D-ResNet)", "14.20 mmHg", "8.12 mmHg", "13.10 / 7.40 mmHg"],
            ["MODEL-05 (+BiGRU+MHSA)", "12.65 mmHg", "7.20 mmHg", "11.45 / 6.55 mmHg"],
            ["MODEL-06-SepHead (Ours)", "11.58 mmHg", "6.70 mmHg", "10.12 / 5.91 mmHg"]
        ],
        highlight_last=True,
        metrics_list=[
            ("Subject-Level SBP / DBP", "10.12 / 5.91 mmHg MAE (Pearson r = 0.388 / 0.355)."),
            ("Progression Delta", "6.70 mmHg SBP MAE reduction over demographic baseline."),
            ("Extractor SNR", "POS = 8.9 dB | TS-CAN = 10.4 dB (Green baseline = 2.4 dB)."),
            ("On-Device Runtime", "120 ms batch inference on mobile CPU with zero frame drops.")
        ]
    )

    # -------------------------------------------------------------------------
    # SLIDE 11: Slide 12: Conclusion remarks & Future Scope of work
    # -------------------------------------------------------------------------
    add_card_grid_slide(
        prs,
        title="Slide 12: Conclusion remarks & Future Scope of work",
        category="Summary & Future Research Roadmap",
        columns=2,
        cards_data=[
            {
                "tag": "SUMMARY",
                "title": "Conclusion Remarks",
                "items": [
                    "Feasibility Confirmed: Smartphone cameras reliably track continuous BP with 10.12 / 5.91 mmHg accuracy.",
                    "Physics-Driven Denoising: POS null space + dual-stream DSP overcomes camera quantization noise.",
                    "Template Collapse Solved: Single-point personal calibration provides hydrostatic anchor meeting ISO 81060-2.",
                    "Edge-Native Delivery: Record-then-Process state machine executes sub-150ms with zero cloud dependency."
                ]
            },
            {
                "tag": "ROADMAP",
                "title": "Future Scope of Work",
                "items": [
                    "Diverse Cohort Trials: Expand testing across diverse Fitzpatrick skin types (I–VI) and clinical hypertension cohorts.",
                    "Multi-Site Optical PTT: Dual-ROI tracking (forehead + palm) to calculate optical Pulse Transit Time for zero-shot calibration.",
                    "Hardware NPU Delegates: Android NNAPI and Qualcomm Hexagon acceleration for sub-50ms continuous streaming.",
                    "Kiosks & Smart Mirrors: Integration into public health triage kiosks and contactless smart bathroom mirrors."
                ]
            }
        ]
    )

    # Save to both outputs
    prs.save(FULL_OUTPUT)
    print(f"Full presentation saved to: {FULL_OUTPUT}")
    prs.save(DOWNLOADS_OUT)
    print(f"Template updated in Downloads: {DOWNLOADS_OUT}")

def main():
    print("="*60)
    print("MODERN DARK MODE TECH PPTX GENERATOR")
    print("="*60)
    build_draft_presentation()
    build_full_vt_presentation()
    print("="*60)
    print("ALL PPTX PRESENTATIONS SUCCESSFULLY COMPILED!")
    print("="*60)

if __name__ == "__main__":
    main()
