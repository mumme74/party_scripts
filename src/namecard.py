from PIL import Image, ImageDraw, ImageFont
from sys import platform
from io import BytesIO
from pathlib import Path
import urllib.error, urllib.request
import configparser, os, zipfile

prj_dir = Path(__file__).parent.parent


dir_path = Path(__file__).absolute().parent

# search paths to find fonts
fontsuffixes = ['','.ttf','.TTF','.otf','.OTF']

fontpaths = [dir_path / "fonts/", '']
if platform == 'darwin': # apple
  fontpaths += ['~/Library/Fonts/', 
               '/System/Library/Fonts/Supplemental/',
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
    with urllib.request.urlopen(params) as resp:
      with zipfile.ZipFile(BytesIO(resp.read())) as z:
        for name in z.namelist():
          n = Path(name)
          if n.suffix.lower() in (".ttf", ".otf") and \
            not name.startswith('.'):
            z.extract(name, dir_path / "fonts/")
            # take a copy of first font to requested fontname
            if not os.path.exists(dir_path / f"fonts/{fontname}{n.suffix}"):
              z.getinfo(name).filename = f"{fontname}{n.suffix}"
              z.extract(name, dir_path / "fonts/")
  except (urllib.error.HTTPError, 
          urllib.error.URLError) as e:
    raise OSError(f"Error fetching font '{fontname}'\n{e}")


def load_font(fontfamily, fontsize, font_download = True):
  for path in fontpaths:
    for suf in fontsuffixes:
      font = os.path.join(path, f"{fontfamily}{suf}")
      try:
        return ImageFont.truetype(font, fontsize)
      except OSError as e:
        pass
  if font_download:
    dl_font(fontfamily)
    return load_font(fontfamily, fontsize, False)
  raise OSError(f"Could not locate font: {fontfamily}, make sure it is installed in your system or select another font.")


def create_name_cards(template, persons, font1, font2 = ''):
    if not font2:
      font2 = font1

    font1 = load_font(font1, 32)
    font2 = load_font(font2, 24)

    w, h = new_size = (600, 400)

    try:
        img = Image.open(template)
        img = img.resize(size=new_size)
    except FileNotFoundError:
        raise Exception(f'Name card template {template} was not found')
    
    for i, p in enumerate(sorted(persons)):
        # create a new image to draw onto
        card = Image.new(mode='RGB', size=new_size, color=(255,255,255,255))
        card.paste(img)
        img_draw = ImageDraw.Draw(card)
        img_draw.rectangle([(0,0),(w-1,h-1)], outline=(0,0,0))
        name = f'{p.fname} {p.lname}'
        dept = f'{p.dept.desc}'
        _, _, w1, h1 = img_draw.textbbox((0,0), name, font1)
        _, _, w2, h2 = img_draw.textbbox((0,0), dept, font2)
        img_draw.text(((w-w1)//2, 270), name, font=font1, fill=(0,0,0))
        img_draw.text(((w-w2)//2, 330), dept, font=font2, fill=(0,0,0))
        card.save(prj_dir / 'outdata' / f'{i}.png')
