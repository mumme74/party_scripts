from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

prj_dir = Path(__file__).parent.parent

def all_png_files():
  return [fn for fn in (prj_dir/'outdata').iterdir() 
            if fn.suffix == '.png']

def create_namecard_docx():
    # Create a new document
    doc = Document()
  
    for png in all_png_files():
        doc.add_picture(str(prj_dir / 'outdata' / png), width=Pt(300))

    # Save the document
    doc.save(prj_dir / 'outdata' / 'namecards.docx')

if __name__ == "__main__":
    create_namecard_docx()