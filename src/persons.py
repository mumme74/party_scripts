from collections import Counter
from .departments import AllDepartments
from .read_data import read_data

class AllPersons:
    def __init__(self, tsv):
        if hasattr(AllPersons, '_instance'):
            raise Exception('AllPersons already instanciated')
        AllPersons._instance = self

        self.tsv = tsv
        self.persons = []
        keys = {
            'date':0, 'mail':1, 'first_name':2, 'last_name': 3, 
            'department':4, 'special_meals':5
        }

        for row in read_data(tsv):
            self.add(row, keys)

    @classmethod
    def ref(cls):
        return cls._instance
    
    def add(self, data, keys):
        "Add a new person"
        p = Person(data, keys)
        self.persons.append(p)
    
    def departments(self):
        "Return count of all departments"
        deps = Counter()
        for p in self.persons:
            deps.update((p.dept,))
        return deps
    
    def special_meals(self):
        "Return all special meals"
        meals = Counter()
        for p in self.persons:
            meals.update((p.special_meals,))
        return meals

class Person:
    def __init__(self, data, keys):
        self.fname = data[keys['first_name']].strip()
        self.lname = data[keys['last_name']].strip()
        self._dept_str = data[keys['department']].strip()
        self.dept = AllDepartments.ref().get_department(self._dept_str)
        self.special_meals = data[keys['special_meals']].strip()
        self.mail = data[keys['mail']].strip()
        self.registered_date = data[keys['date']].strip()

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
