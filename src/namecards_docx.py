from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL

A4_h = Cm(29.7)
A4_w = Cm(21.0)

prj_dir = Path(__file__).parent.parent

def all_png_files():
  return [fn for fn in (prj_dir/'outdata').iterdir() 
            if fn.suffix == '.png']

def create_namecard_docx():
    # Create a new document
    doc = Document()

    # set margins
    for sec in doc.sections:
        sec.top_margin    = Cm(1.5)
        sec.left_margin   = Cm(1.5)
        sec.bottom_margin = Cm(1.5)
        sec.right_margin  = Cm(1.5)
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_height = A4_w
        sec.page_width = A4_h

    #place images in a table for formating 4 on each page
    tbl = doc.add_table(1, 2)
    cells = tbl.rows[0].cells
    for i, png in enumerate(sorted(all_png_files())):
        # format the cell and its paragraph
        cell = cells[i % 2]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        format = p.paragraph_format
        format.space_before = Cm(1.0)
        format.space_after = Cm(0)
        # add new image
        pic = p.add_run().add_picture(str(prj_dir / 'outdata' / png), width=Pt(300))
        if (i+1) % 2 == 0: # add new row each 2nd cell
            cells = tbl.add_row().cells
        
    # Save the document
    doc.save(prj_dir / 'outdata' / 'namecards.docx')

if __name__ == "__main__":
    create_namecard_docx()