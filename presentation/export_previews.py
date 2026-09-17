"""Export ALL slides to PNG using PowerPoint COM automation."""
import comtypes.client
import os
import time

deck_path = os.path.abspath(r"presentation\VT_2026_rPPG_to_BP_Estimation.pptx")
output_dir = os.path.abspath(r"presentation\previews")
os.makedirs(output_dir, exist_ok=True)

print(f"Opening PowerPoint with: {deck_path}")

ppt_app = comtypes.client.CreateObject("PowerPoint.Application")
ppt_app.Visible = True
time.sleep(1)

prs = ppt_app.Presentations.Open(deck_path, ReadOnly=True, WithWindow=False)
time.sleep(2)

total_slides = prs.Slides.Count
print(f"Total slides: {total_slides}")

for slide_num in range(1, total_slides + 1):
    out_path = os.path.join(output_dir, f"slide_{slide_num:02d}.png")
    slide = prs.Slides(slide_num)
    slide.Export(out_path, "PNG", 1920, 1080)
    print(f"  Exported slide {slide_num} -> {out_path}")

prs.Close()
ppt_app.Quit()
print("Done! All slides exported.")
