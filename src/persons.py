from collections import Counter
from datetime import datetime
from .departments import AllDepartments
from .read_data import read_data
from .exceptions import DuplicatePersonException

class AllPersons:
    def __init__(self, project):
        assert not hasattr(AllPersons, '_instance')
        AllPersons._instance = self

        self.unique_check = set()
        self.persons = []

        self.project = project
        self.settings = project.settings['persons']

        for row in read_data(self.settings['file']):
            self.add(row)

    @classmethod
    def ref(cls):
        if not hasattr(cls, '_instance'):
            from .project import Project
            cls._instance = AllPersons(Project.ref().settings)
        return cls._instance
    
    @classmethod
    def reset(cls):
        if hasattr(cls, '_instance'):
            del cls._instance

    def add(self, data):
        "Add a new person"
        p = Person(data, self.settings['hdrs'], 
                   self.settings['nope_expressions'])
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
    def __init__(self, data, keys, no_exprs):
        self.fname = data[keys['fname']].strip()
        self.lname = data[keys['lname']].strip()
        self._dept_str = data[keys['dept']].strip()
        self.dept = AllDepartments.ref().get_department(self._dept_str)
        self.special_foods = data[keys['special_foods']].strip().replace('.','')
        if self.special_foods.lower() in no_exprs:
            self.special_foods = ''
        self.email = data[keys['email']].strip()
        self.registered_date = datetime.strptime(
            data[keys['date']].strip(),
            '%Y-%m-%d %H.%M.%S')
        self.placed_at_tbl = None

    def placed_at_table(self):
        if self.placed_at_table:
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
