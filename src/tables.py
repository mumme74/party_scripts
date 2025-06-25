from pathlib import Path
from .read_data import read_data
from .departments import AllDepartments
from .persons import AllPersons
from .exceptions import DataRetrivalError
from collections import Counter

class AllTables:
    def __init__(self, project):

        self.project = project
        self.settings = project.settings['tables']
        self.data_file = self.settings['file']
        self.tables = []
        self.is_placed = False
        if not self.data_file.name:
            return # when reading an empy project
        self._data = read_data(self.data_file)

        for row in self._data:
            self.tables.append(Table(row, self.project))
    
    def find_table_to(self, num_pers):
        tbls = sorted([(t, t.free_seats()) for t in self.tables], 
                       key=lambda tp: tp[1])
        for t, num in tbls:
            if num >= num_pers:
                return t
        return None
    
    def total_num_seats(self):
        return sum([s.num_seats for s in self.tables])
    
    def place_persons(self):
        "Try to seat all persons at tables with their department"
        all_pers = self.project.persons
        persons = sorted(all_pers.persons)
        deps = all_pers.departments().most_common() # sort largest table first

        if len(persons) > self.total_num_seats():
            raise DataRetrivalError(f'*** Det finns inte tillräckligt med platser, för alla personer!')

        # first place prioritized tables
        for table in [t for t in self.tables if t.prio_dept]:
            for p in persons:
                if not p.placed_at_tbl and p.dept in table.prio_dept:
                    table.place_person(p)

        # find a table for this
        table, pla = None, 1
        while pla: # continue to iterate until all are placed
            pla = 0 
            # loop from department level trying to keep them together
            for dep, num in deps: 
                placed = 0
                for p in filter(lambda p: p.dept.id == dep and \
                                not p.placed_at_tbl, persons):
                    # possibly change table
                    if not table or table.free_seats() == 0:
                        for n in range(num, 0, -1):
                            table = self.find_table_to(n - placed)
                            if table: break

                    if table and table.place_person(p):
                        placed += 1
                        pla += 1
                table = None
            
        # sanity check
        for p in persons:
            assert p.placed_at_tbl

        for t in self.tables:
            print(t.id, t.departments())

        self.is_placed = True

class Table:
    def __init__(self, row, project):
        keys = project.settings['tables']['hdrs']
        self.id = row[keys['id']]
        self.num_seats = int(row[keys['num_seats']])
        self.persons = []
        self.prio_dept = []
        if len(row) >= keys['prio_dept'] + 1:
            for dept in row[keys['prio_dept']].split(' '):
                dep = project.departments.get_department(dept)
                if dep.id == 'unk':
                    raise DataRetrivalError(f'**** {dept} is not among registered departments')
                self.prio_dept.append(dep)

    def departments(self):
        "Return how many persons from each department at this table"
        cnt = Counter()
        for p in self.persons:
            cnt.update((p.dept.name,))
        return cnt
    
    def free_seats(self):
        "Return how many free seats there are left at this table"
        return self.num_seats - len(self.persons)
    
    def place_person(self, person) -> bool:
        "Try to place person at this table, will fail if full"
        assert person.placed_at_tbl == None
        if self.num_seats - len(self.persons) > 0:
            self.persons.append(person)
            person.placed_at_tbl = self
            return True
        return False
