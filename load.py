
def parse_name(name_str):
    split_name = name_str.split('')
    for name in split_name:
        name = name.strip()
    return tuple(split_name)


def load_campers(filename):
    campers = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            campers.append(parse_name(line))
    return campers


def load_counselors(filename):
    tables = []
    counselors = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            table = []
            for name in line.split(','):
                parsed_name = parse_name(name)
                counselors.append(parsed_name)
                table.append(parsed_name)
            tables.append(table)
    return counselors, tables

