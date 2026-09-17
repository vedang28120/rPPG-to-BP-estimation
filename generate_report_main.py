"""
generate_report_main.py
=======================
Master script to assemble and generate the complete Vocational Training Report
in DOCX format (LuminaBP_Vocational_Training_Report.docx) and Markdown format.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Import helper functions
from build_full_report import (
    add_heading_chapter,
    add_heading_sub1,
    add_heading_sub2,
    add_heading_sub3,
    add_body_p,
    add_bullet_p,
    add_equation_block,
    add_figure,
    add_table_custom,
    add_footer_page_num,
    add_page_border,
    remove_page_border,
    set_table_borders
)

# Import chapter builders
from report_sections.front_matter import (
    build_cover_page,
    build_declaration,
    build_certificate,
    build_acknowledgments,
    build_abstract
)
from report_sections.front_matter_lists import (
    build_table_of_contents,
    build_list_of_figures,
    build_list_of_tables,
    build_abbreviations
)
from report_sections.chapter1 import build_chapter1
from report_sections.chapter2 import build_chapter2
from report_sections.chapter3 import build_chapter3
from report_sections.chapter4 import build_chapter4
from report_sections.chapter5 import build_chapter5
from report_sections.chapter6 import build_chapter6
from report_sections.chapter7 import build_chapter7
from report_sections.references import build_references
from report_sections.appendix import build_appendix

def set_section_margins(section, top=0.88, bottom=1.0, left=1.5, right=1.0):
    section.top_margin = Inches(top)
    section.bottom_margin = Inches(bottom)
    section.left_margin = Inches(left)
    section.right_margin = Inches(right)

def main():
    print("Initializing LuminaBP Vocational Training Report Generator...")
    doc = docx.Document()

    # Force Word to auto-update all field codes (PAGE numbers) on open
    settings = doc.settings.element
    update_fields = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    settings.append(update_fields)

    # Normal Style settings
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # -------------------------------------------------------------
    # SECTION 1: COVER PAGE (Bordered, unnumbered)
    # -------------------------------------------------------------
    sect1 = doc.sections[0]
    set_section_margins(sect1, top=0.88, bottom=1.0, left=1.5, right=1.0)
    add_page_border(sect1)
    
    logo_path = 'presentation/assets/college_logo.png'
    build_cover_page(doc, logo_path)

    # -------------------------------------------------------------
    # SECTION 2: PRELIMINARY PAGES (Declaration to Abbreviations)
    # Numbering: Roman lower numerals (i, ii, iii, iv, v, vi, ...)
    # -------------------------------------------------------------
    sect2 = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_margins(sect2, top=0.88, bottom=1.0, left=1.5, right=1.0)
    sect2.header.is_linked_to_previous = False
    sect2.footer.is_linked_to_previous = False
    remove_page_border(sect2)  # Strip inherited cover page border
    add_footer_page_num(sect2, is_roman=True, start_val=1) # Starts at page i

    print("Building Preliminary Pages...")
    build_declaration(doc, add_heading_chapter, add_body_p)
    doc.add_page_break()

    build_certificate(doc, add_heading_chapter, add_body_p)
    doc.add_page_break()

    build_acknowledgments(doc, add_heading_chapter, add_body_p)
    doc.add_page_break()

    build_abstract(doc, add_heading_chapter, add_body_p)
    doc.add_page_break()

    build_table_of_contents(doc, add_heading_chapter, add_table_custom)
    doc.add_page_break()

    build_list_of_figures(doc, add_heading_chapter, add_table_custom)
    doc.add_page_break()

    build_list_of_tables(doc, add_heading_chapter, add_table_custom)
    doc.add_page_break()

    build_abbreviations(doc, add_heading_chapter, add_table_custom)

    # -------------------------------------------------------------
    # SECTION 3: CORE CHAPTERS, REFERENCES & APPENDIX
    # Numbering: Arabic decimal numerals (1, 2, 3, ...)
    # -------------------------------------------------------------
    sect3 = doc.add_section(WD_SECTION.NEW_PAGE)
    set_section_margins(sect3, top=0.88, bottom=1.0, left=1.5, right=1.0)
    sect3.header.is_linked_to_previous = False
    sect3.footer.is_linked_to_previous = False
    remove_page_border(sect3)  # Strip inherited cover page border
    add_footer_page_num(sect3, is_roman=False, start_val=1) # Starts at page 1

    print("Building Chapter 01: Introduction...")
    build_chapter1(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_body_p, add_bullet_p)
    doc.add_page_break()

    print("Building Chapter 02: Vocational Training Curriculum & Foundations...")
    build_chapter2(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_table_custom)
    doc.add_page_break()

    print("Building Chapter 03: Literature Review & Biomedical Signal Analysis...")
    build_chapter3(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom)
    doc.add_page_break()

    print("Building Chapter 04: Proposed Methodology & Architecture...")
    build_chapter4(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom, add_equation_block)
    doc.add_page_break()

    print("Building Chapter 05: Implementation Details & Experimental Protocol...")
    build_chapter5(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom)
    doc.add_page_break()

    print("Building Chapter 06: Experimental Results and Discussion...")
    build_chapter6(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_figure, add_table_custom)
    doc.add_page_break()

    print("Building Chapter 07: Conclusion and Future Work...")
    build_chapter7(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p)
    doc.add_page_break()

    print("Building References...")
    build_references(doc, add_heading_chapter)
    doc.add_page_break()

    print("Building Appendix A: Engineering Architecture & Baseline Specifications...")
    build_appendix(doc, add_heading_chapter, add_heading_sub1, add_heading_sub2, add_heading_sub3, add_body_p, add_bullet_p, add_table_custom)

    # Save document to both filenames
    output_docx = "LuminaBP_Vocational_Training_Report.docx"
    output_docx_editable = "LuminaBP_Vocational_Training_Report_Editable.docx"
    doc.save(output_docx)
    doc.save(output_docx_editable)
    print(f"\n[SUCCESS] Report successfully generated and saved to:")
    print(f"  - {os.path.abspath(output_docx)}")
    print(f"  - {os.path.abspath(output_docx_editable)}")

if __name__ == "__main__":
    main()
