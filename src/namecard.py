from PIL import Image, ImageDraw, ImageFont
from sys import platform
from io import BytesIO
from pathlib import Path
from .exceptions import ReadFileNotFound
import urllib.error, urllib.request
import os, zipfile, re

prj_dir = Path(__file__).parent.parent
dir_path = Path(__file__).absolute().parent

default_sz = (600, 400)

# search paths to find fonts
fontsuffixes = ['','.ttf','.TTF','.otf','.OTF']

fontpaths = [prj_dir / "fonts/"]
if platform == 'darwin': # apple
    fontpaths += ['~/Library/Fonts/', 
                  '/System/Library/Fonts/',
                  '/Library/Fonts/']
elif platform in ('linux', 'linux2'):
    fontpaths += ['~/.local/fonts/', 
                  '/usr/share/fonts/',
                  '/usr/local/share/fonts/',
                  '/usr/share/fonts/truetype/'] 
elif platform == 'win32':
    fontpaths += [f'C:\\Users\\{os.getusername()}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\',
                  'C:\\Windows\\Fonts\\']
else:
    print(f'Unsupported os: {platform}, may not work correctly')


# last resort try to download font and unpack
def dl_font(fontname):
    print(f"Font {fontname} not found, downloading it.")
    font = fontname.lower().replace(' ','-')
    params = urllib.request.Request(
        url=f"https://font.download/dl/font/{font}.zip",
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
            "Referer":"https://www.google.com/",
            "Sec-Ch-Ua-Platform": "\"Windows\"",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
    )

    try:
        with urllib.request.urlopen(params) as resp, \
             zipfile.ZipFile(BytesIO(resp.read())) as z:
            for name in z.namelist():
                n = Path(name)
                if n.suffix.lower() in (".ttf", ".otf") and \
                   not name.startswith('.'):
                    z.extract(name, prj_dir / "fonts/")
                    # take a copy of first font to requested fontname
                    if not os.path.exists(prj_dir / f"fonts/{fontname}{n.suffix}"):
                        z.getinfo(name).filename = f"{fontname}{n.suffix}"
                        z.extract(name, prj_dir / "fonts/")
    except (urllib.error.HTTPError, 
            urllib.error.URLError) as e:
        raise OSError(f"Error fetching font '{fontname}'\n{e}")


def load_font(fontfamily, fontsize, font_download = True):
    # some fonts have space others dont.
    family = fontfamily.lower()
    family2 = family.replace(' ', '')

    def try_font(font):
        try:
            return ImageFont.truetype(font, fontsize)
        except OSError as e:
            return
        
    def find(root, files):
        for file in files:
            f = root / file
            if f.suffix.lower() not in ('','.otf','.ttf','.ttc'):
                continue

            ft = None
            #print(root, f.stem)
            # some fonts have space others dont.
            stem = f.stem.lower()
            if stem == family:
                ft = try_font(Path(root_path) / f.name)
            elif stem.replace(' ','') == family2:
                ft = try_font(Path(root_path) / f.name.replace(' ', ''))
            if ft: return ft

    def walk_dir(root, dirs):
        rot = root
        for d in dirs:
            rot /= d

        for _,cdirs,files in os.walk(rot, followlinks=True):
            ft = find(rot, files)
            if ft: return ft

            for d in cdirs:
                dr = dirs.copy()
                dr.append(d)
                ft = walk_dir(root, dr)
                if ft: return ft

    for root_path in fontpaths:
        ft = walk_dir(Path(root_path), [])
        if ft: return ft

    if font_download:
        dl_font(fontfamily)
        return load_font(fontfamily, fontsize, False)
    raise OSError(f"Could not locate font: {fontfamily}, make sure it is installed in your system or select another font.")

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
