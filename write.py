import pandas as pd

from pathlib import Path  # TODO: remove when paths are configurable


def write_conflicts(filename, conflicts_dict):
    """ Write the conflicts dict to a file

    Args:
        filename (str): The name of the .csv file to save to
        conflicts_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table
    """
    df = pd.DataFrame.from_dict(conflicts_dict, orient='index').T
    df.to_csv(filename, index=False)


def write_week(year, week, tables):
    """ Write the tables for this year and week to a file

    Args:
        year (int): The year of this summer
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
    filename = Path(__file__).parent / 'data' / f'{year}-Week-{week}.csv'
    df.to_csv(filename, index=False)
