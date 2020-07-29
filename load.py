
def _parse_name(name_str):
    """Parses a name from a string with whitespaces, to a tuple of names

    Args:
        name_str (str): A string of a full name. Ex. "Joe Schmo" or
                        " Joe Schmo" or "Joe  Schmo  "

    Returns:
        tuple: A tuple of the form (first_name, last_name)
    """
    split_name = name_str.split(' ')
    for name in reversed(split_name):
        if name == '':
            split_name.remove(name)
    return tuple(split_name)


def load_campers(filename):
    """ Loads a list of campers from a file

    Args:
        filename (str): The name of the .csv file with each camper name
                        on a new line ordered by cabin, mallards to crows

    Returns:
        list: The list of camper names as tuples
    """
    campers = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            campers.append(_parse_name(line))
    return campers


def load_counselors(filename):
    """ Loads a list of couselors and tables from a file

    Args:
        filename (str): The name of the .csv file with each counselor
                        table on a new line, where a table is a comma
                        seperated list of counselors at that table

    Returns:
        tuple: A length two tuple with the following values:
                The list of the counselor names as tuples
                The list of tables, each as a list of occupant
                    name tuples
    """
    tables = []
    counselors = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            table = []
            for name in line.split(','):
                parsed_name = _parse_name(name)
                counselors.append(parsed_name)
                table.append(parsed_name)
            tables.append(table)
    return counselors, tables


if __name__ == "__main__":
    """ Loads counselors, campers, and tables from default file locations
        and then prints them to the console
    """
    from pathlib import Path
    data_directory = Path(__file__).parent / 'data'  # change to configurable

    camper_list_csv = data_directory / 'Camper List - Mallards to Crows.csv'
    campers = load_campers(camper_list_csv)

    counselor_tables_csv = data_directory / 'Counselor Tables.csv'
    counselors, tables = load_counselors(counselor_tables_csv)

    print(campers)
    print(counselors)
    print(tables)
