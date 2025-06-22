from src.read_data import read_data
from src.departments import AllDepartments
from src.persons import AllPersons
from src.tables import AllTables
from src.namecard import create_name_cards
from src.namecards_docx import create_namecard_docx
from src.tables_docx import create_table_report
from src.special_foods import create_special_foods_report
from src.project import Project, NameCard
from src.exceptions import *
from pathlib import Path
from argparse import ArgumentParser

# the root dir of this program
rootdir = Path(__file__).parent

# input arguments
parser = ArgumentParser(prog='Skapa bordsplacerings brickor')
parser.add_argument('--tsv', type=str, help='Path to the source data file for persons', 
                    default=rootdir / 'indata/party.tsv', nargs='?')
parser.add_argument('--party-greet', type=str, help='The greeting printed to namecard',
                    default='Party !', nargs='?')
parser.add_argument('--namecard-template', type=str, help='Path to the template to build each card from',
                    default=rootdir / 'templates/default_namecard.json', nargs='?')
parser.add_argument('--departments', type=str, help='Path to all departments and their synonyms',
                    default=rootdir / 'indata/departments.json', nargs='?')
parser.add_argument('--create-namecards', type=bool, help='Create new namecards',
                    default=True, nargs='?')
parser.add_argument('--place-at-tables', type=bool, default=True, nargs='?',
                    help='Wheather we should place people at their tables')
parser.add_argument('--tables', type=str, help='The path to the source data file for each table',
                    default=rootdir / 'indata/tables.tsv', nargs='?')
parser.add_argument('--table-signs-template-docx', type=bool, help='The path to the template file for eah table',
                    default=rootdir / 'templates/table_sign_default.docx', nargs='?')
parser.add_argument('--special-foods', type=bool, help='Produce a list with all special foods',
                    default=True, nargs='?')
parser.add_argument('project', type=str, help='Path to projectfile',
                    default='', nargs='?')
args = parser.parse_args()

def place_at_tables(project):
    if args.place_at_tables:
        project.tables.place_persons()
        create_table_report(project)

def namecards(project):
    if args.create_namecards:
        if args.place_at_tables:
            pers = [p for t in project.tables.tables for p in t.persons]
        else:
            pers = sorted(project.persons)
        create_name_cards(project, pers)
        create_namecard_docx(project)

def special_foods(project):
    if args.special_foods:
        create_special_foods_report(project)

def dbg_print_dept(project):
    # debug print how many for each dept.
    deps = project.persons.departments()
    for dep, v in deps.most_common():
        print(f'{dep.upper()}: {v}')
    print()

def switches(project):
    s = project.settings
    s['persons']['file'] = args.tsv
    obj = {
        'greet':args.party_greet, 
        'template':args.namecard_template
    }
    s['namecard'] = NameCard(obj)
    s['departments']['file'] = args.departments
    s['tables']['file'] = args.tables
    project.reload()

def main():
    project = Project()
    try:
        if args.project:
            project.open_project(args.project)
        else:
            switches(project)

        dbg_print_dept(project)
        place_at_tables(project)
        namecards(project)
        special_foods(project)

    except (ReadFileException) as e:
        print(f'**File error: {e.file}\n{e}')
    except IOError as e:
        print(f'**IO Error: {e}')
    except AppException as e:
        print(f'**Error: {e}')
    except Exception as e:
        print(f'**Exception: {e}')

if __name__ == '__main__':
    main()
