from sys import platform
from io import BytesIO
from pathlib import Path
from PIL import ImageFont
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord
import urllib.error, urllib.request
import os, zipfile


FAMILY_NAME = 1
SUB_FAMILY_NAME = 2
FULL_FONT_NAME = 4

prj_dir = Path(__file__).parent.parent
dir_path = Path(__file__).absolute().parent
fonts_dir = prj_dir / 'fonts'

# search paths to find fonts
fontsuffixes = ['','.ttf','.TTF','.otf','.OTF']

fontpaths = []
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
    fontpaths += [f'C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\Windows\\Fonts\\',
                  'C:\\Windows\\Fonts\\']
else:
    print(f'Unsupported os: {platform}, may not work correctly')
fontpaths.append(prj_dir / "fonts/") # lookup downloaded fonts last

class DownloadFontBase:
    def __init__(self, fontname, suffix="", pads=None):
        self.fontname = fontname
        self.suffix = suffix
        self.pads = pads if pads else ['','regular','std']
        self.headers = {
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

    def get_font(self):
        return self.fontname.replace(' ','-').lower()

    def download(self):
        for pad in self.pads:
            if pad:
                u = f'{self.url}{self.get_font()}-{pad}{self.suffix}'
            else:
                u = f'{self.url}{self.get_font()}{self.suffix}'

            if self._download(u):
                return True

    def _download(self, url) ->bool:
        print(url)
        params = urllib.request.Request(url=url, headers=self.headers)
        try:
            with urllib.request.urlopen(params) as resp:
                self._handle_response(resp)
                return True
        except (urllib.error.HTTPError,
                urllib.error.URLError) as e:
            return False

    def _handle_response(self, resp):

        if 'application/zip' in resp.headers.get('Content-Type'):
            self._unzip_font(resp)
        else:
            self._save_file(resp)

    def _unzip_font(self, resp):
        with zipfile.ZipFile(BytesIO(resp.read())) as z:
            for name in z.namelist():
                n = Path(name)
                if n and n.suffix.lower() in (".ttf", ".otf") and \
                   not name.startswith('.'):
                    z.extract(name, fonts_dir)
                    filename = Path(z.getinfo(name).filename)
                    fullname = font_fullname(fonts_dir / filename)
                    if fullname and (filename.stem != fullname or filename.parent != fonts_dir):
                        z.getinfo(name).filename = f'{fullname}{filename.suffix}'
                        z.extract(name, fonts_dir)

                    # take a copy of first font to requested fontname
                    if self.fontname and not os.path.exists(
                            fonts_dir / f"{self.fontname}{n.suffix}"):
                        z.getinfo(name).filename = f"{self.fontname}{n.suffix}"
                        z.extract(name, fonts_dir)

    def _save_file(self, resp):
        with(f'fonts/{self.fontname}{self.suffix}', 'wb') as f:
            f.write(resp.read())

    def _copy_file(self, from_, to):
        with open(from_, 'rb') as src, \
             open(to, 'wb') as dst:
            dst.write(src.read())

class Freefontsfamily_org(DownloadFontBase):
    def __init__(self, fontname):
        super().__init__(fontname, ['script'])
        self.url = "https://freefontsfamily.org/download/"

class Legionfonts_com(DownloadFontBase):
    def __init__(self, fontname):
        super().__init__(fontname, ".zip")
        self.url = "https://legionfonts.com/storage/archives/"
        self.times = 3
        self.dash = '-'

    def download(self):
        for i in range(self.times,0,-1):
            if i == 2:
                self.dash = ''
                self.pads = ['ltstd',r'ltstd%20scr']
            elif i == 1:
                self.pads = ['LTStd','LTStd%20Scr']

            for pad in self.pads:

                if pad:
                    u = f'{self.url}{self.get_font()}{self.dash}{pad}{self.suffix}'
                else:
                    u = f'{self.url}{self.get_font()}{self.suffix}'

                if self._download(u):
                    return True
            self.times -= 1


    def get_font(self):
        match self.times:
            case 3:
                return super().get_font()
            case 2:
                return self.fontname.lower().replace(' ','')
            case 1:
                return self.fontname.replace(' ','')

class Font_Download(DownloadFontBase):
    def __init__(self, fontname):
        super().__init__(fontname, ".zip")
        self.url = "https://font.download/dl/font/"

class Fontpalace(DownloadFontBase):
    def __init__(self, fontname):
        super().__init__(fontname)
        self.url = "https://www.fontpalace.com/font-download/"
        self.suffix = ".ttf"

class Mac_fontsGithub(DownloadFontBase):
    loaded = False
    def __init__(self):
        super().__init__('')
        self.url = "https://github.com/codxse/linux-mandatory-font/archive/refs/heads/master.zip"

    def download(self):
        Mac_fontsGithub.loaded = True
        fonts_root = Path('fonts')
        if (fonts_root / 'linux-mandatory-font-master').exists():
            return True

        return super().download()


def font_fullname(path):
    "Reads a fontfile and extracts its name in full"
    font = ttLib.TTFont(path)
    try:
        return font['name'].getDebugName(FULL_FONT_NAME)
    except Exception:
        return Path(path).stem

# last resort try to download font and unpack
def dl_font(fontname):
    print(f"Font {fontname} not found, downloading it.")
    font = fontname.lower().replace(' ','-')

    downloaders = (
        Fontpalace(fontname),
        Legionfonts_com(fontname),
        Freefontsfamily_org(fontname),
        Font_Download(fontname)
    )

    for dl in downloaders:
        if dl.download():
            return True

    raise OSError(f"Error fetching font '{fontname}'")


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
        # start with downloading mac-fonts from https://github.com/codxse/linux-mandatory-font
        if not Mac_fontsGithub.loaded:
            if Mac_fontsGithub().download():
                try:
                    return load_font(fontfamily, fontsize, False)
                except OSError:
                    pass
        dl_font(fontfamily)
        return load_font(fontfamily, fontsize, False)
    raise OSError(f"Could not locate font: {fontfamily}, make sure it is installed in your system or select another font.")