import pandas as pd

from pathlib import Path  # TODO: remove when paths are configurable


def _check_file(filename: str):
    """ Makes sure the file exists

    Args:
        filename (str): The filename to check
    """
    f = Path(filename)
    if not f.exists():
        p = f.parent
        while not p.exists():
            p.mkdir()
            p = p.parent
        f.touch()


def write_conflicts(filename: str, conflicts_dict: dict):
    """ Write the conflicts dict to a file

    Args:
        filename (str): The name of the .csv file to save to
        conflicts_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table
    """
    # _check_file(filename)
    df = pd.DataFrame.from_dict(conflicts_dict, orient='index').T
    df.to_csv(filename, index=False)


def write_week(week: int, tables: list):
    """ Write the tables for this year and week to a file

    Args:
        week (int): The week for the table's
        tables (list): The list of tables, where a table is a list of
                        the Names sitting at it
    """
    tables_dict = {}
    for i, table in enumerate(tables):
        table_name = 'Table ' + str(i+1)
        tables_dict[table_name] = []
        for name in table:
            tables_dict[table_name].append(name.full)
    df = pd.DataFrame.from_dict(tables_dict, orient="index").T
    # TODO: change below to be configurable
    filename = Path(__file__).parent / 'data' / f'Week-{week}.csv'
    
    df.to_csv(filename, index=False)
