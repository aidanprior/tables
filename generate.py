from random import shuffle
from copy import deepcopy

NUM_TABLES = 21
TABLE_SIZE = 10


def _sectionalize_list(num_sections, to_sectionalize):
    """ Splits the to_sectionalize list into a list of sections

    Args:
        num_sections (int): The number of sections to split into
        to_sectionalize (list): A list to split up

    Returns:
        list: A list of length num_sections of sublists sliced from
              the original list
    """
    sections = []
    size = len(to_sectionalize)//num_sections
    for s in range(num_sections):
        if (s+1)*size >= len(to_sectionalize):
            section = to_sectionalize[s*size:]
        else:
            section = to_sectionalize[s*size:(s+1)*size]
        sections.append(section)

    return sections


def conflicts(camper, table, conflict_dict):
    """ Checks to see if the camper conflicts with someone at the table

    Args:
        camper (Name): The camper name to check for conflicts
        table (list): List of Names at the table
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table

    Returns:
        bool: True if the camper conflicts with someone at the table
    """
    for t_name in table:
        if camper.full in conflict_dict:
            if t_name.full in conflict_dict[camper.full]:
                return True
        if t_name.full in conflict_dict:
            if camper.full in conflict_dict[t_name.full]:
                return True

    return False


def seed_camper(camper, in_tables, conflict_dict):
    """ Seeds the camper into a table

    Args:
        camper (Name): The camper to seed into the tables
        in_tables (list): The list of tables, where a table is a list of
                            the Names sitting at it
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table

    Returns:
        list: The new tables list with the camper seeded,
                (bool: False) if the camper couldn't be seeded
    """
    global TABLE_SIZE
    min_size = min([len(table) for table in in_tables])
    if min_size > TABLE_SIZE:
        table_names = ['Table ' + str(i) + "\n" +
                       ''.join(['\t'+name.full+'\n'for name in table])
                       for i, table in enumerate(in_tables)]
        error_string = (
            "current table size is larger than maximum possible table size: "
            f" {min_size = } {TABLE_SIZE = }"
            f" {''.join(table_names)}"
        )
        raise OverflowError(error_string)

    tables = deepcopy(in_tables)

    def seed():
        idxs = list(range(len(tables)))
        shuffle(idxs)
        for i in idxs:
            table = tables[i]
            if len(table) <= min_size:
                if not conflicts(camper, table, conflict_dict):
                    table.append(camper)
                    return tables
        return False

    output = seed()
    if not output:
        min_size += 1
        output = seed()

    return output


def seed_section(in_section, in_tables, conflict_dict):
    """ Seeds the section into tables

    Args:
        in_section (list): A list of lists (each a list of Names),
                            The Names to be seeded into tables
        in_tables (list): The list of tables, where a table is a list of
                            the Names sitting at it
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table

    Returns:
        tuple: A tuple of length two where the first element is a bool
                indicating whether the seed was successful, and the
                second is an iterable. If successful, it is the new
                tables list. Otherwise, it is a Name for the camper
                who could not be seeded.
    """
    tables = deepcopy(in_tables)
    section = deepcopy(in_section)
    shuffle(section)
    for camper in section:
        output = seed_camper(camper, tables, conflict_dict)
        if output:
            tables = output
        else:
            return False, camper
    return True, tables


def seed_aide(aide, in_tables, conflict_dict, aide_idxs):
    """ Seeds the aide into a table

    Args:
        aide (Name): The aide to seed into the tables
        in_tables (list): The list of tables, where a table is a list of
                            the Names sitting at it
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table
        aide_idxs (list): The indexes of the tables where an aide is assigned

    Returns:
        list: The new tables list with the aide seeded,
                (bool: False) if the aide couldn't be seeded
    """
    tables = deepcopy(in_tables)
    idxs = aide_idxs.copy()

    shuffle(idxs)
    for i in idxs:
        table = tables[i]
        if not conflicts(aide, table, conflict_dict):
            table.append(aide)
            return tables
    return False


def seed_aides(in_aides, in_tables, conflict_dict, aide_idxs):
    """ Seeds all the aides into the aide tables

    Args:
        in_aides (list): A list of aide Names
        in_tables (list): The list of tables, where a table is a list of
                            the Names sitting at it
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table
        aide_idxs (list): The indexes of the tables where an aide is assigned

    Returns:
        tuple: A tuple of length two where the first element is a bool
                indicating whether the seed was successful, and the
                second is an iterable. If successful, it is the new
                tables list. Otherwise, it is a Name for the aide
                who could not be seeded.
    """
    tables = deepcopy(in_tables)
    aides = in_aides.copy()
    shuffle(aides)

    for aide in aides:
        output = seed_aide(aide, tables, conflict_dict, aide_idxs)
        if output:
            tables = output
        else:
            return False, aide

    return True, tables


def seed_tables(campers, in_tables, conflict_dict, aides, aide_idxs):
    """ Seed all the campers into the tables

    Args:
        campers (list): A list of camper Names
        in_tables (list): The list of tables, where a table is a list of
                            the Names sitting at it
        conflict_dict (dict): A dictionary with name strings as keys
                                (Ex. "Joe Schmo"), and lists of name
                                strings as the values where the two names
                                cannot sit at the same table

    Returns:
        list: The new tables list
    """
    global NUM_TABLES
    aged_sections = _sectionalize_list(NUM_TABLES, campers)
    sections = deepcopy(aged_sections)
    tables = deepcopy(in_tables)
    shuffle(sections)

    success, output = seed_aides(aides, tables, conflict_dict, aide_idxs)
    if success:
        tables = output
    else:
        print(f"Seed issue: {output.full}")

    for section in sections:
        success, output = seed_section(section, tables, conflict_dict)
        if success:
            tables = output
        else:
            print(f"Seed issue: {output.full}")

    section_totals = []
    for table in tables:
        total = 0
        for name in table:
            for s, section in enumerate(aged_sections):
                if name in section:
                    total += s
                    continue
        section_totals.append(total)
    for i, avg in enumerate(section_totals):
        print(f"Table {i+1}: {avg}")
    print(min(section_totals), max(section_totals))
    return tables


def generate_conflicts(all_names):
    """ Generates a Conflict dict from last names of campers and counselors

    Args:
        all_names (list): A list of all Names (campers, counselors, and aides)

    Returns:
        dict: A dictionary of conflicts where the keys and values
                are full name strings. The values are the other names that
                conflict with key name. However their are no repeats,
                if a name shows up in the list for another name, it won't
                have that other name it its own list (or might not have a list
                at all)
    """
    conflict_dict = {}
    for name in all_names:
        for other in all_names:
            if name == other:
                continue
            if name.last == other.last:
                if name.full not in conflict_dict \
                        and other.full not in conflict_dict:
                    conflict_dict[name.full] = []
                    conflict_dict[name.full].append(other.full)
                elif name.full in conflict_dict:
                    conflict_dict[name.full].append(other.full)
                elif other.full in conflict_dict \
                        and name.full not in conflict_dict[other.full]:
                    conflict_dict[other.full].append(name.full)

    return conflict_dict
