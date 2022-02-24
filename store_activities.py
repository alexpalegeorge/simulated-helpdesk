#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""store_activities.py: Reads a JSON file containing helpdesk tickets, and
inserts them into a newly created SQLite Database."""

__author__ = "Alexander Palegeorge"
__status__ = "Prototype"
__version__ = "01/12/2021"

import sqlite3
import json
import argparse
import os.path

parser = argparse.ArgumentParser(prog="db_gen",
                                 description="Freshdesk database generator")

parser.add_argument("-i",
                    "--input",
                    type=str,
                    required=True,
                    metavar="",
                    help="the name of the JSON file containing activity data")
parser.add_argument("-o",
                    "--output",
                    type=str,
                    required=True,
                    metavar="",
                    help="Output SQLite database name")

args = parser.parse_args()


def run(input_json, output_db):
    """Controls the flow of reading JSON data, creating the entity model, and
    populating it with activity data."""

    json_name = check_input_name(input_json)
    db_name = check_output_name(output_db)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    if check_json_exists(json_name) and not check_db_exists(c, db_name):

        print("Creating database...")

        create_tables(c)
        conn.commit()

        data = load_json(json_name)

        time_ticket_created = data['metadata']['start_at']

        task_value = 50000
        for ticket in data['activities_data']:
            if 'note' in ticket['activity'] \
                    and 'status' not in ticket['activity']:
                insert_ticket(ticket, conn, c, time_ticket_created, 0)
            elif 'note' not in ticket['activity'] \
                    and 'status' in ticket['activity']:
                task_value += 1
                insert_ticket(ticket, conn, c, time_ticket_created, task_value)
            elif 'note' in ticket['activity'] \
                    and 'status' in ticket['activity']:
                task_value += 1
                insert_ticket(ticket, conn, c, time_ticket_created, task_value)

        conn.commit()

        print("Successfully inserted '" + json_name + "' ticket data into new "
              "database, '" + db_name + "'.")

    conn.close()


def check_input_name(filename):
    if filename[-5:] == '.json':
        json_name = filename
    else:
        json_name = filename + '.db'
    return json_name


def check_output_name(filename):
    if filename[-3:] == '.db':
        db_name = filename
    else:
        db_name = filename + '.db'
    return db_name


def check_db_exists(c, dbname):
    """Queries the database connection to check if a table has already been
    created at the given location. Must be parsed the database connection
    cursor object, and the database name."""
    exists = False
    c.execute("""
        SELECT count(name) FROM sqlite_master WHERE type='table' 
        AND name='Tickets'
    """)
    if c.fetchone()[0] == 1:
        exists = True
        print("A database named '" + dbname + "' already exists. You must"
              "delete it or choose a different name to proceed.")
    return exists


def check_json_exists(json_name):
    exists = False
    if os.path.exists(json_name):
        exists = True
    else:
        print("No JSON file named '" + json_name + "' exists. You must"
              "generate it or enter the name of an existing JSON to proceed.")
    return exists


def create_tables(c):
    """Creates the entities and relationships needed for storing activity data.
    Must be parsed the database connection cursor object."""
    c.execute("""
        CREATE TABLE Tickets (
            ticket_id               integer NOT NULL PRIMARY KEY,
            time_ticket_created     text NOT NULL,
            performed_at            text NOT NULL,
            performer_id            integer NOT NULL,
            note_id                 integer,
            task_id                 integer,
            
            FOREIGN KEY(performer_id) REFERENCES Performer(performer_id),
            FOREIGN KEY(note_id) REFERENCES Note(note_id),
            FOREIGN KEY(task_id) REFERENCES Task(task_id)
        )""")
    c.execute("""
        CREATE TABLE Performer (
            performer_id            integer NOT NULL PRIMARY KEY,
            performer_type          text NOT NULL
        )""")
    c.execute("""
        CREATE TABLE Note (
            note_id                 integer NOT NULL PRIMARY KEY,
            note_type               integer NOT NULL,
            ticket_id               integer NOT NULL,
            
            FOREIGN KEY(ticket_id) REFERENCES Ticket(ticket_id)
        )""")
    c.execute("""
        CREATE TABLE Task (
            task_id                 integer NOT NULL PRIMARY KEY,
            shipping_address        text NOT NULL,
            category                text NOT NULL,
            contacted_customer      integer NOT NULL,
            issue_type              text NOT NULL,
            source                  integer NOT NULL,
            status                  text NOT NULL,
            priority                integer NOT NULL,
            task_group              text NOT NULL,
            agent_id                integer NOT NULL,
            requester               integer NOT NULL,
            product                 text NOT NULL,
            ticket_id               integer NOT NULL,
            
            FOREIGN KEY(ticket_id) REFERENCES Ticket(ticket_id)
        )""")


def load_json(json_name):
    with open(json_name) as file:
        data = json.load(file)
    return data


def insert_ticket(ticket, conn, c, time_ticket_created, task_value):
    """Takes data from the ticket dictionary object, and inserts it into the
    correct tables."""

    note_id = None
    task_id = None

    # Foreign keys are added to sub-dictionaries so that they can be easily
    # inserted below
    if 'note' in ticket['activity']:
        note_id = ticket['activity']['note']['id']
        ticket['activity']['note']['ticket_id'] = ticket['ticket_id']

    if task_value > 0:
        task_id = task_value
        ticket['activity']['task_id'] = task_id
        ticket['activity']['ticket_id'] = ticket['ticket_id']

    ticket['note_id'] = note_id
    ticket['task_id'] = task_id
    ticket['time_ticket_created'] = time_ticket_created

    with conn:
        c.execute("""
            INSERT INTO Tickets VALUES (
                :ticket_id,
                :time_ticket_created, 
                :performed_at, 
                :performer_id,
                :note_id,
                :task_id
            )
        """, ticket)
        c.execute("""
            INSERT OR IGNORE INTO Performer VALUES (
                :performer_id,
                :performer_type
            )
        """, ticket)

        if note_id is not None:
            c.execute("""
                INSERT INTO Note VALUES (
                    :id,
                    :type,
                    :ticket_id
                )
            """, ticket['activity']['note'])

        if task_id is not None:
            c.execute("""
                INSERT INTO Task VALUES (
                    :task_id,
                    :shipping_address,
                    :category,
                    :contacted_customer,
                    :issue_type,
                    :source,
                    :status,
                    :priority,
                    :group,
                    :agent_id,
                    :requester,
                    :product,
                    :ticket_id
                )
            """, ticket['activity'])


if __name__ == '__main__':
    run(args.input, args.output)
