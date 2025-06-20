from faker import Faker
from pathlib import Path
from src.persons import Person
fake = Faker(['sv_SE', 'en_GB'])

file_dir = Path(__file__).parent / "data"

class MockDept:
    def __init__(self, id):
        self.id = id
        self.name = f'name_{id}'

class MockAllDepartments:
    def __init__(self, project):
        self.departments = [
            MockDept('unk'),
            MockDept('sale'),
            MockDept('prod'),
            MockDept('mang')
        ]
        self.project = project

    def get_department(self, dept):
        for d in self.departments:
            if dept == d.id:
                return d
        return MockDept('unk')
    
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
    
