from random import shuffle

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
    tables = in_tables.copy()
    shuffle(tables)
    for i, table in enumerate(tables):
        if not conflicts(camper, table, conflict_dict) \
                and len(table) < TABLE_SIZE:
            table.append(camper)
            return tables
    return False


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
    tables = in_tables.copy()
    section = in_section.copy()
    shuffle(section)
    for camper in section:
        output = seed_camper(camper, tables, conflict_dict)
        if output:
            tables = output
        else:
            return False, camper
    return True, tables


def seed_tables(campers, in_tables, conflict_dict):
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
    old_sections = _sectionalize_list(NUM_TABLES, campers)
    sections = old_sections.copy()
    tables = in_tables.copy()
    shuffle(sections)
    for section in sections:
        # print(f"Working on section {old_sections.index(section)}")
        success, output = seed_section(section, tables, conflict_dict)
        if success:
            tables = output
        else:
            print(f"Seed issue: {output.full}")

    return tables


def generate_conflicts(campers, counselors):
    """ Generates a Conflict dict from last names of campers and counselors

    Args:
        campers (list): A list of camper Names
        counselors (list): A list of counselor Names

    Returns:
        dict: A dictionary of conflicts where the keys and values
                are full name strings. The values are the other names that
                conflict with key name. However their are no repeats,
                if a name shows up in the list for another name, it won't
                have that other name it its own list (or might not have a list
                at all)
    """
    conflict_dict = {}
    for name in campers + counselors:
        for other in campers + counselors:
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
