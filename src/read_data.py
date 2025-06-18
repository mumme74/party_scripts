import csv, json
import openpyxl
from pathlib import Path

import openpyxl.utils
import openpyxl.utils.exceptions
from .exceptions import *

def read_data(path: Path) -> list:
    """The root function to read files
    
    Parameter
    ---------
    path: Path
        the path to the file to read

    Returns
    -------
    list: A list of rows

    Raises
    ------
    ReadFileException
    """
    try:
        with open(path, newline='', encoding='utf8') as file:
            return _route_to_reader(path, file)
    except (FileNotFoundError):
        raise ReadFileNotFound(path, f"Could not locate {path}")


def _route_to_reader(path: Path, file):
    match path.suffix:
        case '.csv': return _read_csv(path, file, ';')
        case '.tsv': return _read_csv(path, file, '\t')
        case '.json': return _read_json(path, file)
        case '.xslx': return _read_xlsx(path, file)
        case _: raise ReadFileUnhandledFormat(path, f'{path.suffix} is not handled')

def _read_csv(path, file, delimiter):
    try:
        rows = []
        reader = csv.reader(file, delimiter=delimiter, 
                            quoting=csv.QUOTE_NONE, strict=True)
        hdrs = [k for k in next(reader)]
        def col_from_idx(i):
            return hdrs[i] if i < len(hdrs) else f'Col{i+1}'
        
        # read in all the rows
        for row in reader:
            r = {col_from_idx(i):v for i,v in enumerate(row)}
            if len(r.keys()) < 2:
                raise csv.Error('Bad format')
            rows.append(r)
        return rows
    except csv.Error as e:
        raise ReadFileException(path, f'{e}')

def _read_json(path, file):
    try:
        return json.load(file)
    except json.JSONDecodeError as e:
        raise ReadFileException(path, f'{e}')
    
def _read_xlsx(path, file):
    try:
        frm = openpyxl.load_workbook(path)
        book = frm.active
        rows = []
        for row in book.iter_rows(1, book.max_row):
            for col in book.iter_cols(1, book.max_column):
                rows.append(col[row].value)
        return rows
    except openpyxl.utils.exceptions.InvalidFileException as e:
        raise ReadFileException(path, f'{e}')
