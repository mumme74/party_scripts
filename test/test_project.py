import setup_prj_dir
import unittest, os
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
app_dir = data_dir.parent.parent

class TestTextFont(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.obj = {
            'font':'testfont',
            'size': 10,
            'pos': [10,20],
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
        self.template_png = Path('test_namecard.png')
        self.greet = 'test greet'
        self.obj = {
            'greet': self.greet,
            'template': self.template
        }

    def tearDown(self):
        super().tearDown()
        outdata = data_dir / 'outdata/'
        for root, dirs, files in os.walk(outdata):
            for f in files:
                if not (outdata / f).name.startswith('.'):
                    (outdata / f).unlink(True)

    def test_constructor(self):
        card = NameCard(self.obj)
        self.assertEqual(card.greet, self.greet)
        self.assertEqual(card.template_json, self.template)
        self.assertEqual(card.template_png, self.template_png)
        self.assertEqual(card.tbl_id_text.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 10,
            "pos": [13,3],
            "align": "absolute",
            "color": "#999999",
            "enabled": True
        })
        self.assertEqual(card.greet_text.__json__(),
        {
            "font": "Georgia Italic",
            "size": 32,
            "pos": [400,210],
            "align": "center",
            "color": "#000000",
            "enabled": True
        })
        self.assertEqual(card.name_text.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 32,
            "pos": [400,270],
            "align": "center",
            "color": "#000000",
            "enabled": True
        })
        self.assertEqual(card.dept_text.__json__(),
        {
            "font": "Lucida Handwriting STD",
            "size": 24,
            "pos": [400,320],
            "align": "center",
            "color": "#000000",
            "enabled": True
        })

    def test_fail_construct(self):
        self.obj['template'] = 'nonexistant.json'
        self.assertRaises(ReadFileNotFound,
                          lambda: NameCard(self.obj))

    def test_json(self):
        card = NameCard(self.obj)
        self.maxDiff = None
        obj = card.__json__()
        self.assertEqual(obj['greet'], self.greet)
        self.assertEqual(obj['template'],self.template)
        self.assertTrue('card' in obj)
        c = obj['card']
        self.assertEqual(c['name'], 'Test namecard')
        self.assertEqual(c['template_png'], self.template_png)
        self.assertTrue(isinstance(c['tbl_id_text'], dict))
        self.assertTrue(isinstance(c['greet_text'], dict))
        self.assertTrue(isinstance(c['name_text'], dict))
        self.assertTrue(isinstance(c['dept_text'], dict))

    def test_save_as_new_template(self):
        card = NameCard(self.obj)
        self.assertRaises(
            WriteFileExists,
            lambda: card.save_as_new_template(data_dir / self.template))
        file = data_dir / 'outdata' / f'save_as_{self.template.name}'
        file_png = file.parent / f'save_as_{self.template_png.name}'
        card.save_as_new_template(file)
        self.assertTrue(file.exists())
        self.assertTrue(file_png.exists())

class TestPreject(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.projectfile = data_dir / "test_project.json"
        self.save_as_file = data_dir / "test_project_save_as.json"

    def test_constructor(self):
        now = datetime.now()
        prj = Project()
        self.assertEqual(len(prj.departments.departments), 1)
        self.assertEqual(len(prj.tables.tables), 0)
        self.assertEqual(len(prj.persons.persons), 0)
        s = prj.settings
        self.assertEqual(s['date'].strftime('%Y-%m-%d %H:%M'),
                         now.strftime('%Y-%m-%d %H:%M'))
        self.assertEqual(s['project_name'][:6], 'Party ')
        self.assertEqual(s['project_file_path'], Path(''))
        self.assertEqual(s['output_folder'],
                         app_dir / 'outdata')
        self.assertEqual(s['departments'],{
            'hdrs':{'id':0,'name':1,'syn':2},
            'file':Path('')
        })
        self.assertEqual(s['tables'],{
            'hdrs':{'id':0,'num_seats':1,'prio_dept':2},
            'file':Path('')
        })
        self.assertEqual(s['persons'],{
            'hdrs':{
                'date':0,'email':1,'fname':2,
                'lname':3,'dept':4,'special_foods':5
            },
            'file':Path(''),
            'nope_expressions':['-','--','nej','nope','no','none','inga']
        })
        self.assertTrue(isinstance(s['namecard'],NameCard))
        self.assertEqual(s['table_sign']['file'],
                         app_dir / "templates" / "table_sign_default.docx")

    def test_open_project(self):
        prj = Project()
        self.assertRaises(
            ReadFileNotFound,
            lambda: prj.open_project('nonexistant.json')
        )

        prj.open_project(data_dir / "test_project.json")

if __name__ == "__main__":
    unittest.main()