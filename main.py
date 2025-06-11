from src.read_data import read_data
from src.departments import AllDepartments
from src.persons import AllPersons
from src.namecard import create_name_cards
from src.namecards_docx import create_namecard_docx
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
args = parser.parse_args()

# init singletons
depts = AllDepartments(args.departments)
persons = AllPersons(args.tsv)

# create new namecard images
if args.create_namecards:
    create_name_cards(args.template, persons.persons, "Lucida Handwriting STD")
    create_namecard_docx()


    
