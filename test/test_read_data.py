import setup_prj_dir
import unittest
from src.exceptions import ReadFileException, \
                           ReadFileNotFound, \
                           ReadFileUnhandledFormat
from pathlib import Path
from src.read_data import read_data

file_dir = Path(__file__).parent / "data"

# -------------------------------------

class TestUnhandledFormat(unittest.TestCase):
    def test_fail_bad_format(self):
        path = file_dir / "test_unhandled_format.txt"
        self.assertRaises(ReadFileUnhandledFormat,
                          lambda: read_data(path))

# ------------------------------------

class TestNonExistant(unittest.TestCase):
    def test_fail_nonexisting(self):
        self.assertRaises(ReadFileNotFound, 
                          lambda: read_data('nonexistant'))

# ------------------------------------

class TestCSV(unittest.TestCase):
    def test_fail_wrongformat(self):
        path = file_dir / "test_wrong_format.csv"
        self.assertRaises(ReadFileException,
                          lambda: read_data(path))
        
    def test_open_csv(self):
        path = file_dir / "test.csv"
        rows = read_data(path)
        self.assertEqual(len(rows), 2)
        self.assertCountEqual(rows,[
            {'Hdr1':'row1vlu1','Hdr2':'row1vlu2','Hdr3':'row1vlu3'},
            {'Hdr1':'row2vlu1','Hdr2':'row2vlu2','Hdr3':'row2vlu3','Col4':'row2vlu4'}
        ])
        
# ------------------------------------

class TestTSV(unittest.TestCase):
        
    def test_open_tsv(self):
        path = file_dir / "test.tsv"
        rows = read_data(path)
        self.assertEqual(len(rows), 2)
        self.assertCountEqual(rows,[
            {'Hdr1':'row1vlu1','Hdr2':'row1vlu2','Hdr3':'row1 vlu3'},
            {'Hdr1':'row2 vlu1','Hdr2':'row2 vlu2','Hdr3':'row2 vlu3','Col4':'row2 vlu4'}
        ])

# -----------------------------------

class TestJSON(unittest.TestCase):
    def test_open_json(self):
        path = file_dir / "test.json"
        rows = read_data(path)
        self.assertEqual(len(rows), 3)
        self.assertCountEqual(rows,[
            {'col1':'row1vlu1','col2':'row1vlu2','col3':'row1vlu3'},
            {'col1':'row2vlu1','col2':'row2vlu2','col3':'row2vlu3'},
            {'col1':'row3vlu1','col2':'row3vlu2','col3':'row3vlu3','col4':'row3vlu4'}
        ])

if __name__ == "__main__":
    unittest.main()