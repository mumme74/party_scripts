from PIL import Image, ImageDraw
from pathlib import Path
from .exceptions import ReadFileNotFound
from .fonts import load_font, prj_dir
import os


default_sz = (600, 400)

def clear_old_cards():
    for file in (prj_dir/'outdata').iterdir():
        if file.suffix == '.png' and file.stem.isnumeric():
            os.remove(prj_dir / 'outdata' / file)

def draw_text(font, text, img_draw, new_size):
    if not font.enabled:
        return
    w, h = new_size
    sw, sh = default_sz
    scale_factor = w / sw

    fnt = load_font(font.font, round(font.size*scale_factor))

    match font.align:
        case 'absolute':
            pos = (font.pos[0] * scale_factor,
                   font.pos[1] * scale_factor)
        case 'center' | _ :
            _, _, w1, h1 = img_draw.textbbox((0,0), text, fnt)
            x = font.pos[0] * scale_factor
            pos = (x-(w1 // 2), font.pos[1]*scale_factor)

    img_draw.text(pos, text, font=fnt, fill=font.color)

def create_name_cards(project, persons):
    img, new_size, out_dir, card = load_template(project)

    for i, p in enumerate(persons):
        card_img = create_img(img, card, new_size, p)
        card_img.save(out_dir / f'{i}.png')

def load_template(prj, card=None, new_size=None):
    if not card:
        card = prj.settings['namecard']
    out_dir = prj.settings['output_folder']
    template = Path(card.template_json).parent / \
                 Path(card.template_png).name

    clear_old_cards()
    new_size = default_sz if not new_size else new_size

    try:
        img = Image.open(template)
        img = img.resize(size=new_size)
        return img, new_size, out_dir, card
    except FileNotFoundError:
        raise ReadFileNotFound(f'*** Name card template {template} was not found')

def create_img(img, card, new_size, per):
    w, h = new_size
    # create a new image to draw onto
    card_img = Image.new(mode='RGB', size=new_size, color=(255,255,255,255))
    card_img.paste(img)
    img_draw = ImageDraw.Draw(card_img)
    # draw a outline
    img_draw.rectangle([(0,0),(w-1,h-1)], outline="#000000")

    # draw texts
    draw_text(card.greet_text, card.greet, img_draw, new_size)
    draw_text(card.name_text, f'{per.fname} {per.lname}', img_draw, new_size)
    draw_text(card.dept_text, f'{per.dept.name}', img_draw, new_size)
    draw_text(card.tbl_id_text, per.table().id, img_draw, new_size)
    return card_img
