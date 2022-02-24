This desktop application uses object-oriented programming to generate fake helpdesk tickets, according to a brief provided by a client (redacted), saving them as a .json document.
It then runs a separate Python script that reads the .json data, and then generates a SQLite database containing all of the tickets.
A further SQL query is run to gain insight on ticket data.

Author: Alex Palegeorge
Date completed: 01/12/2021

--------------------------

Application contents:
1. ticket_gen.py (random ticket generation script, produces a JSON file)
2. store_activities.py (loads tickets from a JSON file and inserts them into a new SQLite3 database)
3. ticket_status.sql (adds a new entity to the database named 'StatusTime', containing information about ticket status duration in seconds)
4. _freshdesk.bat (for automatically executing items 1, 2, and 3 in order, on Windows)


Launch Instructions (Windows):
1. Ensure Python3 and SQLite3 are installed, and added to PATH.
2. Double click '_freshdesk.bat' inside the 'app' directory.