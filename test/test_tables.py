import setup_prj_dir
import unittest
from pathlib import Path
from collections import Counter
from src.tables import Table, AllTables
from src.exceptions import InputDataBadFormat
from src.read_data import Data, DataRow
from mocks import *

file_dir = Path(__file__).parent / "data"
test_data = file_dir / "test_tables.csv"

class TestTable(unittest.TestCase):
    def mock_persons(self):
        for i in range(7):
            p = MockPerson(self.project)
            p.dept = self.project.departments.departments[i % 4]
            self.project.persons.persons.append(p)

    def setUp(self):
        super().setUp()
        self.project = MockProject()
        self.project.persons = MockAllPersons(self.project)
        self.project.departments = MockAllDepartments(self.project)
        self.data = Data()
        self.data.headers = ('id','num_seats','prio_dept')
        self.data.rows = [
            DataRow(self.data, ('tbl1','10')),
            DataRow(self.data, ('tbl2','20','sale')),
            DataRow(self.data, ('tbl3','30','prod adm'))
        ]

    def test_constructor(self):
        tbl = Table(self.data.rows[0], self.project)
        self.assertEqual(tbl.id, 'tbl1')
        self.assertEqual(tbl.num_seats, 10)
        self.assertEqual(tbl.prio_dept, [])

        tbl2 = Table(self.data.rows[1], self.project)
        self.assertEqual(tbl2.id, 'tbl2')
        self.assertEqual(tbl2.num_seats, 20)
        self.assertEqual(tbl2.prio_dept[0].id, 'sale')

        tbl3 = Table(self.data.rows[2], self.project)
        self.assertEqual(tbl3.id, 'tbl3')
        self.assertEqual(tbl3.num_seats, 30)
        self.assertEqual(tbl3.prio_dept[0].id, 'prod')
        self.assertEqual(tbl3.prio_dept[1].id, 'adm')

    def test_place_person(self):
        self.mock_persons()
        tbl = Table(self.data.rows[0], self.project)
        self.assertEqual(tbl.free_seats(), 10)
        for p in self.project.persons.persons:
            tbl.place_person(p)
            self.assertEqual(p.table(), tbl)
        self.assertEqual(tbl.free_seats(), 3)

    def test_departments(self):
        tbl = Table(self.data.rows[0], self.project)
        self.mock_persons()
        for p in self.project.persons.persons:
            tbl.place_person(p)
        cnt = Counter({'name_unk':2,'name_sale':2,
                       'name_prod':2,'name_maint':1})
        self.assertCountEqual(tbl.departments(), cnt)

if __name__ == '__main__':
    unittest.main()
