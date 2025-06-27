from datetime import datetime
from pathlib import Path
import contextlib
from .exceptions import InputDataBadFormat

def parse_date(date_str, file):
    for ds in ['%Y-%m-%d %H.%M.%S',
               '%Y-%m-%d %H:%M:%S',
               '%Y-%m-%dT%H.%M.%SZ',
               '%Y-%m-%d',
               '%d/%m/%Y']:
        try:
            return datetime.strptime(date_str.strip(),ds)
        except ValueError:
            pass
    raise InputDataBadFormat(file, f'Could not convert date, invalid format {date_str}')

def to_int(vlu, default):
    """Convert to int, use default if fails"""
    try:
        return int(vlu)
    except ValueError:
        return default
    
def file_version_name(dir, filename):
    """Make sure it we get correct version name"""
    filename = Path(filename)
    ver, ext = '', filename.suffix
    filename = filename.stem
    dir = Path(dir)

    while (dir / f'{filename}{ver}{ext}').exists():
        if ver == '':
            ver = 0
        ver += 1
    return f'{filename}{ver}{ext}'


class File(object):
    def __init__(self, path, *args, **kwargs):

        search = [Path('')]
        if 'search' in kwargs:
            search.extend(kwargs['search'])
            del kwargs['search']

        pth = Path(path)

        if pth.is_dir():
            raise FileNotFoundError(f'File {path} was not found.')
        if pth.is_absolute:
            self._f = open(pth, *args, **kwargs)
            return
        
        for p in search:
            try:
                self._f = open(p / pth, *args, **kwargs)
                return
            except FileNotFoundError:
                pass
        raise FileNotFoundError(f'File {path} was not found.')
    
    def __enter__(self):
        return self._f
    
    def __exit__(self, type, vlu, trace):
        self._f.close()
        