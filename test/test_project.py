import setup_prj_dir
import unittest
from pathlib import Path
from datetime import datetime
from collections import Counter
from src.project import Project, TextFont, NameCard
from src.exceptions import InputDataBadFormat, \
                           WriteFileException, \
                           WriteFileExists, \
                           ReadFileNotFound
from src.read_data import Data, DataRow
from mocks import *

data_dir = Path(__file__).parent / "data"

class TestTextFont(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.obj = {
            'font':'testfont',
            'size': 10,
            'pos': (10,20),
            'align': 'center',
            'color': '#CCCCCC',
            'enabled': False
        }
        self.file = 'template.json'

    def test_constructor(self):
        font = TextFont(self.obj, self.file)
        o = self.obj
        self.assertEqual(font.font, o['font'])
        self.assertEqual(font.size, o['size'])
        self.assertEqual(font.pos, o['pos'])
        self.assertEqual(font.align, o['align'])
        self.assertEqual(font.color, o['color'])
        self.assertEqual(font.enabled, o['enabled'])

    def test_construct_fail1(self):
        self.obj['pos'] = False
        self.assertRaises(
            InputDataBadFormat,
            lambda: TextFont(self.obj, self.file)
        )
    
    def test_construct_fail2(self):
        del self.obj['font']
        self.assertRaises(
            InputDataBadFormat,
            lambda: TextFont(self.obj, self.file)
        )

    def test_json(self):
        font = TextFont(self.obj, self.file)
        self.assertEqual(font.__json__(), self.obj)

class TestNameCard(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.template = data_dir / 'test_namecard.json'
        self.greet = 'test greet'

    def tearDown(self):
        super().tearDown()
        save_as = data_dir / f'save_as_{self.template.name}'
        save_as.unlink(True)


    def test_constructor(self):
        card = NameCard(self.greet, self.template)
        self.assertEqual(card.greet, self.greet)
        self.assertEqual(card.template_json, self.template)
        self.assertEqual(card.template_png, 'test_namecard.png')
        self.assertEqual(card.tbl_font.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 10,
            "pos": (13,3),
            "align": "absolute",
            "color": "#999999",
            "enabled": True 
        })
        self.assertEqual(card.greet_font.__json__(),
        {
            "font": "Georgia Italic",
            "size": 32,
            "pos": (400,270),
            "align": "center",
            "color": "#000000",
            "enabled": True 
        })
        self.assertEqual(card.name_font.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 32,
            "pos": (400,270),
            "align": "center",
            "color": "#000000",
            "enabled": True 
        })
        self.assertEqual(card.dept_font.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 24,
            "pos": (400,330),
            "align": "center",
            "color": "#000000",
            "enabled": True 
        })

    def test_fail_construct(self):
        self.assertRaises(ReadFileNotFound,
                          lambda: NameCard(self.greet, 'nonexistant.json'))

    def test_json(self):
        card = NameCard(self.greet, self.template)
        self.assertEqual(card.__json__(),
        {
            'greet':self.greet,
            'template_json':self.template
        })

    def test_save_as_new_template(self):
        card = NameCard(self.greet, self.template)
        self.assertRaises(
            WriteFileExists,
            lambda: card.save_as_new_template(data_dir / self.template))
        file = data_dir / f'save_as_{self.template.name}'
        card.save_as_new_template(file)
        self.assertTrue(file.exists())

class TestPreject(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.projectfile = data_dir / "test_project.json"
        self.save_as_file = data_dir / "test_project_save_as.json"

    def test_constructor(self):
        prj = Project()
        self.assertEqual(prj.departments, None)
        self.assertEqual(prj.tables, None)
        self.assertEqual(prj.persons, None)
        s = prj.settings
        self.assertAlmostEqual(s['date'], datetime.now())
        self.assertEqual(s['project_name'][:6], 'Party ')
        self.assertEqual(s['project_file_path'], '')

    def test_open_project(self):
        pass

if __name__ == "__main__":
    unittest.main()