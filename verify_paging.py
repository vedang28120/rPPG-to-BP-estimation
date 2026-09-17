"""
verify_paging.py
Verifies the complex field codes and updateFields setting in the generated DOCX.
"""
import docx
from lxml import etree

doc = docx.Document('LuminaBP_Vocational_Training_Report.docx')
ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

print('='*60)
print('PAGING VERIFICATION')
print('='*60)

# 1. Check updateFields in document settings
settings = doc.settings.element
update_fields = settings.findall(f'{ns}updateFields')
if update_fields:
    val = update_fields[0].get(f'{ns}val', 'not set')
    print(f'\n[OK] updateFields found: val="{val}"')
else:
    print('\n[FAIL] updateFields NOT found in settings!')

# 2. Check footer field codes for each section
for i, sect in enumerate(doc.sections):
    print(f'\n--- Section {i} Footer ---')
    
    # Check pgNumType
    sectPr = sect._sectPr
    pgNumType = sectPr.xpath('w:pgNumType')
    if pgNumType:
        fmt = pgNumType[0].get(f'{ns}fmt', 'N/A')
        start = pgNumType[0].get(f'{ns}start', 'N/A')
        print(f'  pgNumType: fmt={fmt}, start={start}')
    else:
        print(f'  pgNumType: NONE (no page numbering)')
    
    # Check footer content
    footer = sect.footer
    if footer.is_linked_to_previous:
        print(f'  Footer: LINKED to previous section')
        continue
    
    for fp in footer.paragraphs:
        # Look for fldChar elements (complex field codes)
        fld_chars = fp._p.findall(f'.//{ns}fldChar')
        instr_texts = fp._p.findall(f'.//{ns}instrText')
        fld_simples = fp._p.findall(f'.//{ns}fldSimple')
        
        if fld_chars:
            types = [fc.get(f'{ns}fldCharType', '?') for fc in fld_chars]
            print(f'  [OK] Complex field codes found: {types}')
        if instr_texts:
            instrs = [it.text for it in instr_texts]
            print(f'  [OK] instrText content: {instrs}')
        if fld_simples:
            print(f'  [WARN] fldSimple still present (old approach)')
        
        # Check text runs
        texts = [r.text for r in fp.runs if r.text]
        if texts:
            print(f'  Run texts: {texts}')

# 3. Check page borders
print('\n--- Page Borders ---')
for i, sect in enumerate(doc.sections):
    borders = sect._sectPr.xpath('w:pgBorders')
    has_border = len(borders) > 0
    expected = (i == 0)  # Only section 0 should have borders
    status = 'OK' if has_border == expected else 'FAIL'
    print(f'  Section {i}: borders={has_border} [{status}]')

print('\n' + '='*60)
print('VERIFICATION COMPLETE')
print('='*60)
