# used once to create a couple of hundred persons
from pathlib import Path
from faker import Faker
from faker.providers import DynamicProvider
import sys
fake = Faker(["sv_SE"])

depts = [
    "prod","Manufacture","Assembly", "Factory worker",
    "maint","Mechanic","Maintence",
    "adm","Administration","Economy",
    "sale","sales","seller"
]

test_data_dir = Path(__file__).parent / "data"
if len(sys.argv) > 1:
    test_persons_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        depts.clear()
        depts.extend(sys.argv[2:])
else:
    test_persons_file = test_data_dir / "test_persons.tsv"

special_dept_provider = DynamicProvider(
    "special_depts", depts
)
fake.add_provider(special_dept_provider)

special_food_provider = DynamicProvider(
    "special_meals",
    [
        "","","","","","","","","nut","nöt","seafood","lactosfri",
        "glutenfri","fisk","pescatarian"
    ]
)
fake.add_provider(special_food_provider)

def create_person():
    return (
        fake.past_datetime().strftime("%Y-%m-%d %H:%M:%S"),
        fake.email(),
        fake.first_name(),
        fake.last_name(),
        fake.special_depts(),
        fake.special_meals()
    )

def write_line(file, lst):
    ln = "\t".join(lst)
    file.write(f"{ln}\n")

def main():
    with open(test_persons_file, mode="w", encoding="utf8") as file:
        write_line(file, ["date","email","fname","lname","dept","special foods"])
        for i in range(234):
            write_line(file, create_person())



if __name__ == "__main__":
    main()