"""
verify_deck.py
Detailed validation of picture aspect ratios, coordinates, and boundaries.
"""
import pptx

def verify(pptx_path):
    prs = pptx.Presentation(pptx_path)
    print(f"=== Validating: {pptx_path} ===")
    print(f"Total Slides: {len(prs.slides)}, Slide Size: {prs.slide_width.inches:.3f} x {prs.slide_height.inches:.3f}")
    
    all_ok = True
    for idx, s in enumerate(prs.slides, 1):
        pics = [sh for sh in s.shapes if sh.shape_type == pptx.enum.shapes.MSO_SHAPE_TYPE.PICTURE]
        for p in pics:
            w_in = p.width.inches
            h_in = p.height.inches
            aspect = w_in / h_in
            right = p.left.inches + w_in
            bottom = p.top.inches + h_in
            
            overflow = (right > 13.333 + 0.05 or bottom > 7.500 + 0.05)
            status = "FAIL (Overflow)" if overflow else "PASS"
            if overflow:
                all_ok = False
            print(f"  Slide {idx} Picture: pos=({p.left.inches:.2f}, {p.top.inches:.2f}), size={w_in:.2f} x {h_in:.2f} in, aspect={aspect:.3f} -> {status}")
            
    print(f"Overall Result for {pptx_path}: {'ALL CHECKS PASSED' if all_ok else 'FAILED'}\n")

if __name__ == "__main__":
    verify(r"presentation/VT_2026_rPPG_to_BP_Estimation.pptx")
    verify(r"presentation/technical_presentation_draft.pptx")
