# A project is one specific party
from .persons import AllPersons
from .tables import AllTables
from .departments import AllDepartments
from .exceptions import ReadFileNotFound, \
                        ReadFileException
from datetime import datetime
from pathlib import Path
import json

app_dir = Path(__file__).parent.parent

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
            'templates':{
                'namecard': {
                    'file': str(app_dir / "templates" / "default_namecard.png"),
                    'greet': def_name,
                    'greet_font':{
                        'family':'Georgia Italic',
                        'size':32,
                        'pos_y':210
                    },
                    'name_font':{
                        'family':'Lucinda Handwriting STD',
                        'size':32,
                        'pos_y':270
                    },
                    'dept_font':{
                        'family':'Lucinda Handwriting STD',
                        'size':24,
                        'pos_y':330
                    }
                },
                'table_sign':{
                    'file':str(app_dir / "templates" / "table_sign_default.docx")
                }
            }
        }

        self.departments = None
        self.tables = None
        self.persons = None
    
    @classmethod
    def ref(cls):
        if not cls._instance:
            cls._instance = Project()
        return cls._instance

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
            json.dump(self.settings, file, ensure_ascii=False)

    def save_project(self):
        self.save_project_as(self.settings['project_file_path'])
