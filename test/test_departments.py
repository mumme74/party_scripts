import setup_prj_dir
import unittest
from pathlib import Path
from src.departments import Dept, AllDepartments
from src.exceptions import InputDataBadFormat

file_dir = Path(__file__).parent / "data"
test_data = file_dir / "test_departments.xlsx"

class TestDept(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.dep = Dept("keY","DeSc",["SynOnymS","syn"])
    
    def test_constructor(self):
        self.assertEqual(self.dep.id,"key")
        self.assertEqual(self.dep.name, "DeSc")
        self.assertCountEqual(self.dep.synonyms,
                              ["synonyms","syn"])
        
    def test_match(self):
        self.assertTrue(self.dep.match("KEy"))
        self.assertTrue(self.dep.match("DeSc"))
        self.assertFalse(self.dep.match("non"))
        self.assertTrue(self.dep.match("syn"))
        self.assertTrue(self.dep.match("SynonYms"))

        self.assertFalse(self.dep.match("non"))

    def test_eq(self):
        o = Dept("key","DeSc",["1","2"])
        self.assertTrue(self.dep == o)
        self.assertFalse(self.dep == Dept("n","no",[]))
        self.assertTrue(self.dep == "key")
        self.assertFalse(self.dep == "n")
    
    def test_lt(self):
        o = Dept("k","d",["1","2"])
        self.assertTrue(self.dep < o)
        o.name = "DeSb"
        self.assertFalse(self.dep < o)

    def test_gt(self):
        o = Dept("k","d",["1","2"])
        self.assertFalse(self.dep > o)
        o.name = "DeSb"
        self.assertTrue(self.dep > o)

# ------------------------------------

class TestAllDepartments(unittest.TestCase):
    def setUp(self):
        super().setUp()
        AllDepartments.reset()

    def test_constructor_default(self):
        dep = AllDepartments(test_data)
        self.assertEqual(len(dep.departments), 5)
        for i,d in enumerate(['unk','prod','maint','adm','sale']):
            self.assertEqual(dep.departments[i], d)

    def test_constructor_headers(self):
        hdrs = {'id':'fail','name':'no_name','syn':'other'}
        self.assertRaises(InputDataBadFormat,
                          lambda: AllDepartments(test_data, hdrs))

    def test_get_department(self):
        dep = AllDepartments(test_data)
        self.assertEqual("prod", dep.get_department("Production").id)
        self.assertEqual("prod", dep.get_department("fActorY WoRker").id)
        self.assertEqual("unk", dep.get_department("Dont_find").id)

if __name__ == '__main__':
    unittest.main()
