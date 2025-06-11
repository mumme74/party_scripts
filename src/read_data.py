import csv

def read_data(tsv_file):
    try:
        rows = []
        with open(tsv_file, newline='') as f:
            reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
            next(reader)
            for row in reader:
                rows.append([v for v in row])
            return rows
    except (FileNotFoundError):
        print(f"Could not locate {tsv_file}")
