from pathlib import Path
from .read_data import read_data
from .exceptions import InputDataBadFormat, \
                        DataRetrivalError

class AllDepartments:
    def __init__(self, project):

        # default self.departments include unknown
        self.project = project
        dept = project.settings['departments']
        self.departments = [Dept('unk', 'Unknown', [])]
        self.data_file = dept['file']
        try:
            self._data = read_data(self.data_file)
            for row in self._data:
                key = row[dept['hdrs']['id']]
                name = row[dept['hdrs']['name']]
                syn = row[dept['hdrs']['syn']]
                if not isinstance(syn, (list, tuple)):
                    syn = [s for i, s in enumerate(row.data) 
                        if s and i not in [dept['hdrs']['id'],
                                     dept['hdrs']['name']]]
                self.departments.append(Dept(key, name, syn))
        except (KeyError, DataRetrivalError) as e:
            raise InputDataBadFormat(self.data_file, f'Input data, bad format {e}')
    
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
