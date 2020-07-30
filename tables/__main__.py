
if __name__ == "__main__":
    import load
    import generate
    import write

    from pathlib import Path
    from argparse import ArgumentParser

    # Load the names and empty tables
    campers, counselors, tables, aides, aide_idxs = load.main()

    # Create a simplistic conflicts file if it doesn't exist, otherwise load it
    conflicts_file = Path(__file__).parent / 'data' / 'Conflicts.csv'
    print(conflicts_file.resolve())
    if not conflicts_file.exists():
        print("Generating Conflicts...")
        conflicts_dict = generate.generate_conflicts(campers + counselors +
                                                     aides)
        write.write_conflicts(str(conflicts_file), conflicts_dict)
        exit(0)
    else:
        conflicts_dict = load.load_conflicts(str(conflicts_file))

    # Seed the tables!
    new_tables = generate.seed_tables(campers, tables, conflicts_dict, aides,
                                      aide_idxs)

    # Parse the commandline arguments for the week number
    parser = ArgumentParser(prog="Tables Generator",
                            description="A tables generator for camp")
    parser.add_argument("week", metavar="W", type=int,
                        help="The week used to name the output file")
    args = parser.parse_args()

    # Create the week's table file
    write.write_week(args.week, new_tables)
