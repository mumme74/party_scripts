# A project is one specific party
from .persons import AllPersons
from .tables import AllTables
from .departments import AllDepartments
from .exceptions import ReadFileNotFound, \
                        ReadFileException, \
                        ReadFileUnhandledFormat, \
                        InputDataBadFormat, \
                        WriteFileException, \
                        WriteFileExists
                        
from datetime import datetime
from pathlib import Path
import json

app_dir = Path(__file__).parent.parent

class TextFont:
    def __init__(self, obj, file):
        try:
            self.font  = obj['font']
            self.size  = obj['size']
            self.pos   = tuple(obj['pos'])
            self.align = obj['align']
            self.color = obj['color']
            self.enabled = obj['enabled']
        except (KeyError, ValueError, TypeError) as e:
            raise InputDataBadFormat(
                file, f'Bad format for font {e}')

    def __json__(self):
        return {
            'font':    self.font, 
            'size':    self.size,
            'pos':     self.pos,
            'align':   self.align,
            'color':   self.color,
            'enabled': self.enabled
        }

class NameCard:
    def __init__(self, greet, template):
        self.greet = greet
        self.template_json = template
        try:
            with open(template, encoding='utf8') as file:
                obj = json.load(file)
        except FileNotFoundError as e:
            raise ReadFileNotFound(template, f'Could not find file {e}')
        except json.JSONDecodeError as e:
            raise ReadFileUnhandledFormat(template, f'{e}')
        else:
            self.read_template(obj, template)

    def read_template(self, obj, template):
        self.name = obj['name']
        self.template_png = obj['png_file']
        self.tbl_font = TextFont(
            obj['tbl_id_font'], template)
        self.greet_font = TextFont(
            obj['greet_font'], template)
        self.name_font = TextFont(
            obj['name_font'], template)
        self.dept_font = TextFont(
            obj['dept_font'], template)
        png = Path(template).parent / Path(self.template_json).name
        if not png.exists():
            raise ReadFileNotFound(str(png), f'Template png file {png} does not exist')
        
    def save_as_new_template(self, save_path):
        if Path(save_path).exists():
            raise WriteFileExists(save_path, f'Template file already exists: {save_path}')
        try:
            with open(save_path, encoding='utf8',
                      mode='w') as file:
                json.dump({
                    'name':self.name,
                    'template_png': self.template_png,
                    'tbl_id_font': self.tbl_font,
                    'greet_font': self.greet_font,
                    'name_font': self.name_font,
                    'dept_none': self.dept_font
                }, file, ensure_ascii=False, indent=2,
                  default=lambda o: o.__json__()
                    if hasattr(o, '__json__') else None)
        except IOError as e:
            raise WriteFileException(save_path, f'Failed to save namecard template {e}')

    def __json__(self):
        return {
            'greet': self.greet,
            'template_json': self.template_json
        }

class Project:
    def __init__(self):
        def_name = f'Party {datetime.now().strftime('%Y-%m-%d %H-%M')}'
        self.settings = {
            'date': datetime.now(),
            'project_name': def_name,
            'project_file_path': '',
            'output_folder': app_dir / 'outdata',
            'departments':{
                 # reading order for department columns in file
                'hdrs': {'id':0, 'name':1, 'syn':2},
                # indata file
                'file': ''
            },
            'tables':{
                # reading order for tables file
                'hdrs': {'id':0, 'num_seats':1, 'prio_dept':2},
                # indata file
                'file': ''
            },
            'persons':{
                # reading order for persons file
                'hdrs': {'date':0,'email':1,'fname':2,'lname':3,'dept':4,'special_foods':5},
                # indata file
                'file': '',
                'nope_expressions':['-', '--', 'nej', 'nope','no','none','inga']
            },
            'namecard': NameCard(
                'Party #1', 
                str(app_dir / 'templates' / 'default_namecard.json')
            ),
            'table_sign':{
                'file':str(app_dir / "templates" / "table_sign_default.docx")
            }
        }

        self.departments = None
        self.tables = None
        self.persons = None

    def open_project(self, prj_file):
        try:
            with open(prj_file, encoding='utf8') as file:
                obj = json.load(file)
        except FileNotFoundError:
            raise ReadFileNotFound(prj_file, f'File: {prj_file} not found')
        except json.JSONDecodeError as e:
            raise ReadFileException(prj_file, f'{e}')
        
        def recurse(setting, obj):
            def do(k): # change value or recurse
                if isinstance(setting[k], (list, dict)):
                    recurse(setting[k], obj[k])
                else:
                    setting[k] = obj[k]

            # make sure to only set those values which match type and name
            if isinstance(setting, dict):
                for k,v in setting.items():
                    if hasattr(obj, k) and type(v) == type(obj[k]):
                        do(k)
            elif isinstance(setting, list):
                for i, v in enumerate(setting):
                    if len(obj) > i and type(v) == type(obj[i]):
                        do(i)
        
        # re-load the data with the new settings
        recurse(self.settings, obj)
        self.settings['project_file_path'] = prj_file
        if not self.settings['output_folder']:
            self.settings['output_folder'] = Path(prj_file).parent
        self.reload()

    def reload(self):
        self.departments = AllDepartments(self)
        self.persons = AllPersons(self)
        self.tables = AllTables(self)

    def save_project_as(self, save_path):
        self.settings['project_file_path'] = save_path
        with open(save_path, mode='w') as file:
            json.dump(self.settings, file, 
                      ensure_ascii=False, indent=2,
                      default=lambda o: o.__json__() 
                        if hasattr(o, '__json__') else None)

    def save_project(self):
        self.save_project_as(self.settings['project_file_path'])
