from pathlib import Path
from .read_data import read_data
from .exceptions import InputDataBadFormat

def_hdrs = {
    'id': 'ID',
    'name':'Name',
    'syn': 'Synonyms'
}

class AllDepartments:
    def __init__(self, data_file, hdrs=def_hdrs):
        # singleton
        assert not hasattr(AllDepartments, '_instance')
        AllDepartments._instance = self

        # default self.departments include unknown
        self.departments = [Dept('unk', 'Unknown', [])]
        self.data_file = data_file
        try:
            for row in read_data(data_file):
                key = row[hdrs['id']]
                name = row[hdrs['name']]
                syn = [row[k] for k in row.keys() 
                    if k not in ['id', 'name'] and row[k]]
                self.departments.append(Dept(key, name, syn))
        except KeyError as e:
            raise InputDataBadFormat(data_file, f'Input data, bad format {e}')
        
    @classmethod
    def ref(cls):
        return cls._instance
    
    @classmethod
    def reset(cls):
        if hasattr(cls, '_instance'):
            del cls._instance
    
    def get_department(self, str):
        for d in self.departments:
            if d.match(str):
                return d
        print(f'Department "{str}" was not found')
        return self.departments[0] # unknown
    
class Dept:
    def __init__(self, id, name, synonyms):
        self.id = id.lower()
        self.name = name
        self.synonyms = [s.lower() for s in synonyms]

    def match(self, str):
        "Test if str matches this department"
        key = str.lower().strip()
        if key in self.synonyms or \
           key == self.id or \
           key == self.name.lower():
            return True
        return False
    
    def __eq__(self, o):
        if isinstance(o, str):
            return self.id == o
        return self.id == o.id
    
    def __lt__(self, o):
        return self.name < o.name

    def __gt__(self, o):
        return self.name > o.name
