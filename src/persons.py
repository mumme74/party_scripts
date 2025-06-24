from collections import Counter
from datetime import datetime
from .departments import AllDepartments
from .read_data import read_data
from .helpers import parse_date
from .exceptions import DuplicatePersonException, \
                        InputDataBadFormat

class AllPersons:
    def __init__(self, project):

        self.unique_check = set()
        self.persons = []

        self.project = project
        self.settings = project.settings['persons']

        self._data = read_data(self.settings['file'])
        for row in self._data:
            self.add(row)

    def add(self, data):
        "Add a new person"
        p = Person(data, self.project)
        if (p.fname, p.lname, p.email) in self.unique_check:
            raise DuplicatePersonException(p, f'Duplicate entry of person {p.fname} {p.lname}  {p.email}')
        self.unique_check.add( (p.fname, p.lname, p.email))
        self.persons.append(p)
    
    def departments(self):
        "Return count of all departments"
        deps = Counter()
        for p in self.persons:
            deps.update((p.dept.id,))
        return deps
    
    def special_foods(self):
        "Return all special foods"
        foods = Counter()
        for p in self.persons:
            foods.update((p.special_foods,))
        return foods

class Person:
    def __init__(self, data, project):
        keys = project.settings['persons']['hdrs']
        no_exprs = project.settings['persons']['nope_expressions']
        self.fname = data[keys['fname']].strip()
        self.lname = data[keys['lname']].strip()
        self._dept_str = data[keys['dept']].strip()
        self.dept = project.departments.get_department(self._dept_str)
        self.special_foods = data[keys['special_foods']].strip().replace('.','')
        if self.special_foods.lower() in no_exprs:
            self.special_foods = ''
        self.email = data[keys['email']].strip()
        self.registered_date = parse_date(
            data[keys['date']].strip(),
            project.settings['persons']['file'])
        self.placed_at_tbl = False

    def table_id(self):
        if self.placed_at_tbl:
            return self.placed_at_tbl.id
        return ""


    # for comparisons
    def __eq__(self, o):
        return self.dept == o.dept and \
               self.fname == o.fname and \
               self.lname == o.lname
    
    def __le__(self, o):
        if self.dept > o.dept:
            return True
        elif self.dept == o.dept:
            if self.fname == o.fname:
                return self.lname < o.lname
            return self.fname < o.fname
        return False
    
    def __gt__(self, o):
        if self.dept > o.dept:
            return True
        elif self.dept == o.dept:
            if self.fname == o.fname:
                return self.lname > o.lname
            return self.fname > o.fname
        return False
