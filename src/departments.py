from pathlib import Path
import json

class AllDepartments:
    def __init__(self, synonym_json):
        # singleton
        assert not hasattr(AllDepartments, '_instance')
        AllDepartments._instance = self

        self.departments = [Dept('unk', 'Unknown', [])]
        self.synonym_json = synonym_json
        self._read_json()
    
    def _read_json(self):
        try:
            with open(self.synonym_json) as f:
                for key, val in json.load(f).items():
                    d = Dept(key, val['desc'], val['syn'])
                    self.departments.append(d)
        except FileNotFoundError:
            print(f'Failed to load department file: {self.synonym_json}')
        except (json.JSONDecodeError) as e:
            print(f"Failed to parse json file {self.synonym_json}\n{e}")
        
    @classmethod
    def ref(cls):
        return cls._instance
    
    def get_department(self, str):
        for d in self.departments:
            if d.match(str):
                return d
        print(f'Department "{str}" was not found')
        return self.departments[0] # unknown
    
class Dept:
    def __init__(self, key, desc, synonyms):
        self.key = key
        self.desc = desc
        self.synonoyms = [s.lower() for s in synonyms]

    def match(self, str):
        "Test if str mathes this department"
        key = str.lower().strip()
        if key in self.synonoyms or \
           key == self.key or \
           key == self.desc.lower():
            return True
        return False
    
    def __eq__(self, o):
        return self.desc == o.desc
    
    def __lt__(self, o):
        return self.desc < o.desc

    def __gt__(self, o):
        return self.desc > o.desc