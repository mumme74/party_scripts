from src.read_data import read_data
from src.departments import AllDepartments
from src.persons import AllPersons
from src.tables import AllTables
from src.namecard import create_name_cards
from src.namecards_docx import create_namecard_docx
from src.tables_docx import create_table_report
from src.special_foods import create_special_foods_report
from pathlib import Path
from argparse import ArgumentParser

# the root dir of this program
rootdir = Path(__file__).parent

# input arguments
parser = ArgumentParser(prog='Skapa bordsplacerings brickor')
parser.add_argument('--tsv', type=str, help='Path to the source data file for persons', 
                    default=rootdir / 'indata/party.tsv', nargs='?')
parser.add_argument('--template', type=str, help='Path to the template to build each card from',
                    default=rootdir / 'templates/default.png', nargs='?')
parser.add_argument('--departments', type=str, help='Path to all departments and their synonyms',
                    default=rootdir / 'templates/dept_synonyms.json', nargs='?')
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
args = parser.parse_args()

# init singletons
depts = AllDepartments(args.departments)
persons = AllPersons(args.tsv)

if args.place_at_tables:
    tables = AllTables(args.tables)
    tables.place_persons()
    create_table_report(args.table_signs_template_docx)

# create new namecard images
if args.create_namecards:
    if args.place_at_tables:
        pers = [p for t in AllTables.ref().tables for p in t.persons]
    else:
        pers = sorted(persons.persons)
    create_name_cards(args.template, pers, "Lucida Handwriting STD")
    create_namecard_docx()

if args.special_foods:
    create_special_foods_report()