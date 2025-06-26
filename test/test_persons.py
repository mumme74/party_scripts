import setup_prj_dir
import unittest
from pathlib import Path
from faker import Faker
from random import randint
from collections import Counter
from src.persons import Person, AllPersons
from src.exceptions import InputDataBadFormat, \
                           DuplicatePersonException
from src.read_data import Data, DataRow
from mocks import *

fake = Faker(['sv_SE', 'en_GB'])

def mock_person_data(project):
    return [
        fake.past_datetime().strftime('%Y-%m-%d %H.%M.%S'),
        fake.email(),
        fake.first_name(),
        fake.last_name(),
        project.departments.departments[randint(0,3)].id,
        fake.word()]

class TestPerson(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project = MockProject()
        self.project.departments = MockAllDepartments(self.project)
        self.project.tables

    def test_constructor(self):
        data = mock_person_data(self.project)
        p = Person(data, self.project)
        self.assertEqual(p.registered_date.strftime('%Y-%m-%d %H.%M.%S'),
                         data[0])
        self.assertEqual(p.email, data[1])
        self.assertEqual(p.fname, data[2])
        self.assertEqual(p.lname, data[3])
        self.assertEqual(p.dept.id, data[4])
        self.assertEqual(p.special_foods, data[5])
        self.assertEqual(p._placed_at_tbl, None)

    def test_table(self):
        data = mock_person_data(self.project)
        p = Person(data, self.project)
        self.assertEqual(p.table(), None)
        tbl = MockTable(self.project)
        p._placed_at_tbl = tbl
        self.assertEqual(p.table(), tbl)

class TestAllPersons(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.project = MockProject()
        self.project.tables = MockAllTables(self.project)
        for i in range(20):
            self.project.tables.tables.append(MockTable(self.project))

        self.project.departments = MockAllDepartments(self.project)

    def test_contructor(self):
        per = AllPersons(self.project)
        self.assertEqual(len(per.persons), 234)

    def test_add_duplicate(self):
        per = AllPersons(self.project)
        p = per.persons[0]
        data = [
            p.registered_date.strftime('%Y-%m-%d %H:%M:%S'),
            p.email, p.fname, p.lname, 
            p.dept.id, p.special_foods
        ]
        self.assertRaises(
            DuplicatePersonException,
            lambda: per.add(data))
        
    def test_departments(self):
        per = AllPersons(self.project)
        d = per.departments()
        self.assertCountEqual(d.keys(),[
            'maint', 'prod', 'adm', 'sale'])
        self.assertEqual(d, {
            'maint':60,'prod':61,'adm':45,'sale':68
        })

    def test_special_foods(self):
        per = AllPersons(self.project)
        f = per.special_foods()
        self.assertCountEqual(f.keys(),[
            '','nut','nöt','seafood','lactosfri',
            'glutenfri','fisk','pescatarian'])
        self.assertEqual(f, {
            '':27,'nut':34,'nöt':27,''
            'seafood':26,'lactosfri':42,
            'glutenfri':26,'fisk':30,
            'pescatarian':22
        })

if __name__ == "__main__":
    unittest.main()