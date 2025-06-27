# A project is one specific party
from .helpers import parse_date, File
from .persons import AllPersons
from .tables import AllTables
from .departments import AllDepartments
from .exceptions import ReadFileNotFound, \
                        ReadFileException, \
                        ReadFileUnhandledFormat, \
                        InputDataBadFormat, \
                        WriteFileException, \
                        WriteFileExists, \
                        OutdataDirDoesNotExist, \
                        AppException
                        
from datetime import datetime
from pathlib import Path
import json

app_dir = Path(__file__).parent.parent

# an encoder to help encode custom classes to json
class EncodeJson(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        elif isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, Path):
            return str(o)
        return super().default(o)

# A class for each text in namecard
class TextFont:
    def __init__(self, obj, file):
        try:
            self.font  = obj['font']
            self.size  = obj['size']
            self.pos   = list(obj['pos'])
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
    def __init__(self, obj):
        self.greet = obj['greet']
        template = self.template_json = Path(obj['template'])

        if 'card' in obj:
            self.read_object(obj['card'], template)
            return
        
        # else read from template
        try:
            with File(template, encoding='utf8',
                      search=[app_dir]) as file:
                obj = json.load(file)
        except FileNotFoundError as e:
            raise ReadFileNotFound(template, f'Could not find file {e}')
        except json.JSONDecodeError as e:
            raise ReadFileUnhandledFormat(template, f'{e}')
        else:
            self.read_object(obj, template)

    def read_object(self, obj, template):
        self.name = obj['name']
        self.template_png = Path(obj['template_png'])
        self.tbl_id_text = TextFont(
            obj['tbl_id_text'], template)
        self.greet_text = TextFont(
            obj['greet_text'], template)
        self.name_text = TextFont(
            obj['name_text'], template)
        self.dept_text = TextFont(
            obj['dept_text'], template)
        png = Path(template).parent / Path(self.template_json).name
        if not png.exists():
            raise ReadFileNotFound(str(png), f'Template png file {png} does not exist')
        
    def save_as_new_template(self, save_path):
        save_path = Path(save_path)
        if save_path.exists():
            raise WriteFileExists(save_path, 
                f'File {save_path} already exists')
        try:
            with open(save_path, encoding='utf8',
                      mode='w') as file:
                json.dump(self, file, ensure_ascii=False, indent=2,
                    cls=EncodeJson)

            # copy over the image to
            new_path = save_path.parent / f'{save_path.stem}{self.template_png.suffix}'
            orig_path = self.template_json.parent / self.template_png.name
            if not new_path.exists() and orig_path.exists():
                with open(orig_path, 'br') as from_, \
                     open(new_path, 'bw') as to:
                    to.write(from_.read())

        except IOError as e:
            raise WriteFileException(save_path, f'Failed to save namecard template {e}')

    def __json__(self):
        return {
            'greet': self.greet,
            'template': self.template_json,
            'card': {
                'name': self.name,
                'template_png': self.template_png,
                'tbl_id_text': self.tbl_id_text.__json__(),
                'greet_text': self.greet_text.__json__(),
                'name_text': self.name_text.__json__(),
                'dept_text': self.dept_text.__json__()
            }
        }

class Project:
    def __init__(self):
        def_name = f'Party !'
        self.settings = {
            'date': datetime.now(),
            'project_name': def_name,
            'project_file_path': Path(''),
            'output_folder': app_dir / 'outdata',
            'departments':{
                 # reading order for department columns in file
                'hdrs': {'id':0, 'name':1, 'syn':2},
                # indata file
                'file': Path('')
            },
            'tables':{
                # reading order for tables file
                'hdrs': {'id':0, 'num_seats':1, 'prio_dept':2},
                # indata file
                'file': Path('')
            },
            'persons':{
                # reading order for persons file
                'hdrs': {'date':0,'email':1,'fname':2,'lname':3,'dept':4,'special_foods':5},
                # indata file
                'file': Path(''),
                'nope_expressions':['-', '--', 'nej', 'nope','no','none','inga']
            },
            'namecard': NameCard({
                'greet':'Party #1', 
                'template':app_dir / 'templates' / 'default_namecard.json'
            }),
            'table_sign':{
                'file':app_dir / "templates" / "table_sign_default.docx"
            },
            'persons_placed_hashes': {}
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
                elif isinstance(setting[k], NameCard):
                    setting[k] = NameCard(obj[k])
                elif isinstance(setting[k], datetime):
                    setting[k] = parse_date(obj[k], prj_file)
                elif isinstance(setting[k], Path):
                    setting[k] = Path(obj[k])
                elif type(setting[k]) == type(obj[k]):
                    setting[k] = obj[k]

            # make sure to only set those values which match type and name
            if isinstance(setting, dict):
                for k,v in setting.items():
                    if k in obj:
                        do(k)
            elif isinstance(setting, list):
                for i, v in enumerate(setting):
                    if len(obj) > i and type(v) == type(obj[i]):
                        do(i)
        
        # re-load the data with the new settings
        recurse(self.settings, obj)
        self.settings['project_file_path'] = Path(prj_file)
        self.settings['persons_placed_hashes'] = obj.get('persons_placed_hashes', {})
        self._sanity_check()
        self.reload()

    def _sanity_check(self):
        sett = self.settings
        for obj in [sett['departments'],
                    sett['tables'],
                    sett['persons'],
                    sett['table_sign']]:
            if not Path(obj['file']).exists():
                raise ReadFileNotFound(obj['file'], f'File not found {obj['file']}')

    def reload(self, obj=None):
        props = {
            'departments':AllDepartments,
            'persons':    AllPersons,
            'tables':     AllTables
        }
        for prop, cls in props.items():
            if obj and obj != prop:
                continue

            try:
                self.__dict__[prop] = cls(self)
            except AppException as e:
                # force an instance by omitting file
                file = self.settings[prop]['file']
                self.settings[prop]['file'] = Path()
                self.__dict__[prop] = cls(self)
                self.settings[prop]['file'] = file
                raise e # notify upstream of the error
            
        # rewire placements
        placements = self.settings['persons_placed_hashes']
        for per in self.persons.persons:
            key = f'{per.email}_{per.fname}_{per.lname}'
            if key in placements:
                id = placements[key]
                tbl = next((t for t in self.tables.tables if t.id==id), None)
                if tbl:
                    tbl.place_person(per)

    def save_project_as(self, save_path):
        self.settings['project_file_path'] = save_path
        # store placements already done
        placements = self.settings['persons_placed_hashes']
        for per in self.persons.persons:
            tbl = per.table()
            if tbl:
                key = f'{per.email}_{per.fname}_{per.lname}'
                placements[key] = tbl.id

        # dump settings to json file
        with open(save_path, mode='w') as file:
            json.dump(self.settings, file, 
                      ensure_ascii=False, indent=2,
                      cls=EncodeJson)

    def save_project(self):
        path = self.settings['project_file_path']
        if path:
            self.save_project_as(path)
