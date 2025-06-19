from pathlib import Path
from .read_data import read_data
from .departments import AllDepartments
from .persons import AllPersons
from collections import Counter


class AllTables:
    def __init__(self, table_tsv):
        assert not hasattr(AllTables, '_instance')
        AllTables._instance = self

        self.tsv = table_tsv
        self.tables = []
        self.is_placed = False
        keys = {'ID':0, 'num_seats':1, 'prio_dept':2}

        for row in read_data(table_tsv):
            self.tables.append(Table(row, keys))

    @classmethod
    def ref(cls):
        return cls._instance
    
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
        all_pers = AllPersons.ref()
        persons = sorted(all_pers.persons)
        deps = all_pers.departments().most_common() # sort largest table first

        if len(persons) > self.total_num_seats():
            print(f'*** Det finns inte tillräckligt med platser, för alla personer!')
            exit(1)

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
                for p in filter(lambda p: p.dept.key == dep and \
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
    def __init__(self, row, keys):
        self.id = row[keys['ID']]
        self.num_seats = int(row[keys['num_seats']])
        self.persons = []
        self.prio_dept = []
        if len(row) >= keys['prio_dept'] + 1:
            for dept in row[keys['prio_dept']].split(' '):
                dep = AllDepartments.ref().get_department(dept)
                if dep.id == 'unk':
                    print(f'**** {dept} is not among registered departments')
                    exit(1)
                self.prio_dept.append(dep)

    def departments(self):
        "Return how many persons from each department at this table"
        cnt = Counter()
        for p in self.persons:
            cnt.update((p.dept.desc,))
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
