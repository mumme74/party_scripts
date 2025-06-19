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
        data = read_data(path)
        self.assertEqual(len(data), 2)
        self.assertCountEqual(data.headers,
            ('Hdr1','Hdr2','Hdr3','Col4'))
        for i, row in enumerate([
            {'Hdr1':'row1vlu1','Hdr2':'row1vlu2','Hdr3':'row1vlu3'},
            {'Hdr1':'row2vlu1','Hdr2':'row2vlu2','Hdr3':'row2vlu3','Col4':'row2vlu4'}
        ]):
            for k,v in row.items():
                self.assertEqual(data[i][k], v)

        
# ------------------------------------

class TestTSV(unittest.TestCase):
        
    def test_open_tsv(self):
        path = file_dir / "test.tsv"
        data = read_data(path)
        self.assertEqual(len(data), 2)
        self.assertCountEqual(data.headers,
            ('Hdr1','Hdr2','Hdr3','Col4'))
        for i, row in enumerate([
            {'Hdr1':'row1vlu1','Hdr2':'row1vlu2','Hdr3':'row1 vlu3'},
            {'Hdr1':'row2 vlu1','Hdr2':'row2 vlu2','Hdr3':'row2 vlu3','Col4':'row2 vlu4'}
        ]):
            for k,v in row.items():
                self.assertEqual(data[i][k], v)


# -----------------------------------

class TestJSON(unittest.TestCase):
    def test_open_json(self):
        path = file_dir / "test.json"
        data = read_data(path)
        self.assertEqual(len(data), 3)
        self.assertCountEqual(data.headers,
            ('col1','col2','col3','col4'))
        for i, row in enumerate([
            {'col1':'row1vlu1','col2':'row1vlu2','col3':'row1vlu3'},
            {'col1':'row2vlu1','col2':'row2vlu2','col3':'row2vlu3'},
            {'col1':'row3vlu1','col2':'row3vlu2','col3':'row3vlu3','col4':'row3vlu4'}
        ]):
            for k,v in row.items():
                self.assertEqual(data[i][k], v)

            

# ----------------------------------
class TestXLSX(unittest.TestCase):
    def test_open_json(self):
        path = file_dir / "test.xlsx"
        data = read_data(path)
        self.assertEqual(len(data), 3)
        self.assertCountEqual(data.headers,
            ('col1','col2','col3','Col4'))
        for i, row in enumerate([
            {'col1':'row1vlu1','col2':'row1vlu2','col3':'row1vlu3','Col4':None},
            {'col1':'row2vlu1','col2':'row2vlu2','col3':'row2vlu3','Col4':None},
            {'col1':'row3vlu1','col2':'row3vlu2','col3':'row3vlu3','Col4':'row3vlu4'}
        ]):
            for k,v in row.items():
                self.assertEqual(data[i][k], v)

if __name__ == "__main__":
    unittest.main()