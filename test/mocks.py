from faker import Faker
from pathlib import Path
from random import randint
from src.persons import Person
fake = Faker(['sv_SE', 'en_GB'])

file_dir = Path(__file__).parent / "data"

class MockDept:
    def __init__(self, id, synonyms=[]):
        self.id = id
        self.name = f'name_{id}'
        self.synonyms = [s.lower() for s in synonyms]

class MockAllDepartments:
    def __init__(self, project):
        self.departments = [
            MockDept('unk'),
            MockDept('sale',['sales','seller']),
            MockDept('prod',['production','manufacture','assembly','Factory worker']),
            MockDept('maint',['maintenence','mechanic','maintence']),
            MockDept('adm',['administration','economy'])
        ]
        self.project = project

    def get_department(self, dept):
        dept = dept.lower()
        for d in self.departments:
            if dept == d.id or dept==d.name or \
               dept in d.synonyms:
                return d
        return self.departments[0] # unk
    
class MockProject:
    def __init__(self):
        self.departments = None
        self.persons = None
        self.tables = None
        self.settings = {
            'tables': {
                'hdrs':{'id':0,'num_seats':1,'prio_dept':2},
                'file':file_dir / "test_tables.csv"
            },
            'departments': {
                'hdrs':{'id':0,'name':1,'syn':2},
                'file':file_dir / "test_departments.xlsx"
            },
            'persons':{
                 # reading order for persons file
                'hdrs': {'date':0,'email':1,'fname':2,'lname':3,'dept':4,'special_foods':5},
                # indata file
                'file': file_dir / 'test_persons.tsv',
                'nope_expressions':['-', '--', 'nej', 'nope','no','none','inga']
            
            }
        }

class MockAllPersons:
    def __init__(self, project):
        self.persons = []
        self.project = project


class MockPerson:
    def __init__(self, project):
        self.fname = fake.first_name()
        self.lname = fake.last_name()
        self.email = fake.email()
        self.dept = None
        self.special_foods = fake.get_words_list()
        self.registered_date = fake.date()
        self.placed_at_tbl = None

    def table_placement(self):
        if self.placed_at_table:
            return self.placed_at_table.id
        return ""
    
class MockTable:
    _tbl_cnt = 1
    def __init__(self, project):
        self.id = f"Table {MockTable._tbl_cnt}"
        MockTable._tbl_cnt += 1
        self.num_seats = randint(4,12)
        self.persons = []
        self.prio_dept = []
    
class MockAllTables:
    def __init__(self, project):
        self.tables = []
        self.project = project
        self.is_placed = False

