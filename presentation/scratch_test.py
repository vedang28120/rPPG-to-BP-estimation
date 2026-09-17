"""Generate slide preview images using python-pptx + PIL rendering."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

# Just print out the shape information for key slides so we can understand the layout
deck_path = r"c:\Users\simpl\.antigravity-ide\Projects\rPPG to BP estimation\presentation\VT_2026_rPPG_to_BP_Estimation.pptx"
prs = Presentation(deck_path)

for idx, slide in enumerate(prs.slides):
    print(f"\n{'='*60}")
    print(f"SLIDE {idx+1} ({len(slide.shapes)} shapes)")
    print(f"{'='*60}")
    for shape in slide.shapes:
        l = shape.left / 914400 if shape.left else 0
        t = shape.top / 914400 if shape.top else 0
        w = shape.width / 914400 if shape.width else 0
        h = shape.height / 914400 if shape.height else 0
        name = shape.shape_type
        has_text = hasattr(shape, 'text_frame') and shape.text_frame.text.strip()
        text_preview = shape.text_frame.text[:60].replace('\n', ' ') if has_text else ""
        print(f"  {name:30s} pos=({l:.2f}, {t:.2f}) size={w:.2f}x{h:.2f}  | {text_preview}")
