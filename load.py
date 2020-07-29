import pandas as pd
from collections import namedtuple

Name = namedtuple("Name", "first last full")


def _parse_name(name_str):
    """Parses a name from a string with whitespaces

    Args:
        name_str (str): A string of a full name. Ex. "Joe Schmo" or
                        " Joe Schmo" or "Joe  Schmo  "

    Returns:
        Name: A namedtuple with first, last, and full as values
    """
    split_name = name_str.split(' ')

    first, *_, last = [name.strip() for name in split_name if name != '']
    full = ' '.join((first, last))

    return Name(first, last, full)


def load_campers(filename):
    """ Loads a list of campers from a file

    Args:
        filename (str): The name of the .csv file with each camper name
                        on a new line ordered by cabin, mallards to crows

    Returns:
        list: The list of camper Names
    """
    campers = []
    df = pd.read_csv(filename, header=None)
    for row in df.itertuples(index=False):
        parsed_name = _parse_name(row[0])
        campers.append(parsed_name)
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
                The list of tables, each as a list of occupant Names
    """
    tables = []
    counselors = []

    df = pd.read_csv(filename, header=None)
    for row in df.itertuples(index=False):
        table = []
        for name in row:
            parsed_name = _parse_name(name)
            counselors.append(parsed_name)
            table.append(parsed_name)
        tables.append(table)

    return counselors, tables


def load_conflicts(filename):
    """ Load the conflicts from a file

    Args:
        filename (str): The name of the .csv file with the conflicts

    Returns:
        dict: A dictionary with name strings as keys
                (Ex. "Joe Schmo"), and lists of name
                strings as the values where the two names
                cannot sit at the same table
    """
    df = pd.read_csv(filename, header=None)
    return df.to_dict(orient='list')


def main():
    """ Loads counselors, campers, tables, and conflict_dict from default file
        locations

    Returns:
        tuple: A tuple of length 3 with the following values:
                A list of camper Names
                A list of counselor Names
                A list of table lists of Names
    """
    from pathlib import Path
    # TODO: change below to be configurable
    data_directory = Path(__file__).parent / 'data'

    camper_list_csv = data_directory / 'Camper List.csv'
    campers = load_campers(camper_list_csv)

    counselor_tables_csv = data_directory / 'Counselor Tables.csv'
    counselors, tables = load_counselors(counselor_tables_csv)

    return campers, counselors, tables


if __name__ == "__main__":
    """ Prints the loaded data
    """
    campers, counselors, tables = main()
    print("campers")
    for camper in campers:
        print(f'\t{camper.full}')
    print("counselors")
    for counselor in counselors:
        print(f'\t{counselor.full}')
    print("tables")
    for table in tables:
        print(f'\t{table}')
