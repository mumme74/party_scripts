from src.read_data import read_data
from src.departments import AllDepartments
from src.persons import AllPersons
from src.namecard import create_name_cards
from pathlib import Path
from argparse import ArgumentParser
import sys

# the root dir of this program
rootdir = Path(__file__).parent

# input arguments
parser = ArgumentParser(prog='Skapa bordsplacerings brickor')
parser.add_argument('--tsv', type=str, help='Path to the source data file for persons', 
                    default=rootdir / 'indata/party.tsv', nargs='?')
parser.add_argument('--template', type=str, help='Path to the template to build each card from',
                    default=rootdir / 'templates/default.png', nargs='?')
parser.add_argument('--departments', type=str, help='Path to all departments and thier synonyms',
                    default=rootdir / 'templates/dept_synonyms.json', nargs='?')
args = parser.parse_args()

# init singletons
depts = AllDepartments(args.departments)
persons = AllPersons(args.tsv)

create_name_cards(args.template, persons.persons, "Lucida Handwriting STD")
