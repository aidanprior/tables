# tables
A tables generator for camp


The script requires multiple csv files as data input:
    "Camper List.csv": A single column row-list of camper names by age
    "Counselor Tables.csv": A row-list of counselors at each table, with a seperate column for each counselor
                            Aides may be included as 'Aide', with a list of Aides at the bottom of the table lists,
                            With one line inbetween with a the 'Aides:' header.
                          
The script will generate a "Conflicts.csv" file if one does not yet exist, where each column will be a list of 
    campers and counselors with the same last name.
    These lists may be added to, removed from, or even new lists added to
  
If the "Conflicts.csv" file already exists, then the script will use those conflicts to generate a week of tables
    and save it in a "Week-#.csv" file where the week number is provided by via commandline arguments
