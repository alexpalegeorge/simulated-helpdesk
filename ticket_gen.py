#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""ticket_gen.py: Creates a JSON file containing the specified number of
randomly generated helpdesk tickets."""

__author__ = "Alexander Palegeorge"
__status__ = "Prototype"
__version__ = "1/12/2021"

import json
import argparse
import random as r
from datetime import datetime, timedelta, timezone

parser = argparse.ArgumentParser(prog="ticket_gen",
                                 description="Freshdesk ticket generator")

parser.add_argument("-n",
                    "--number",
                    type=int,
                    required=True,
                    metavar="",
                    help="Number of tickets to generate.")
parser.add_argument("-o",
                    "--output",
                    type=str,
                    required=True,
                    metavar="",
                    help="Output Json file name")

args = parser.parse_args()


def run(number, output):
    """Runs the ticket generation program, if the parsed arguments are
    valid. """

    try:
        if number_is_valid(number):

            print("Generating tickets...")

            g = Generator()
            report = g.generate_report(number)
            create_file(output, report)

            print("Successfully saved", number, "random tickets to '" +
                  output + "'.")

    except ValueError:
        print('Number of tickets must be "1" or greater.')


class Report:
    """Defines the report structure that lists all added tickets."""

    def __init__(self):
        self.metadata = \
            {
                "start_at": "",
                "end_at": "",
                "activities_count": 0
            }
        self.activities_data = []
        self.report = \
            {
                "metadata": self.metadata,
                "activities_data": self.activities_data
            }

    def add_ticket(self, new_ticket):
        self.activities_data.append(new_ticket)

    def create_report(self, date_range):
        """Once all activities have been added, as well as a time span, this
        function can be called to return the full report in dictionary format."""

        self.metadata["activities_count"] = len(self.activities_data)
        self.metadata["start_at"] = date_range[0].strftime("%d-%m-%Y %X %z")
        self.metadata["end_at"] = date_range[1].strftime("%d-%m-%Y %X %z")
        return self.report


class Ticket:
    """Defines the ticket structure. Tickets can be added to a Report."""

    def __init__(self,
                 performed_at,
                 ticket_id,
                 performer_type,
                 performer_id,
                 activity):
        self.ticket = \
            {
                "performed_at": performed_at,
                "ticket_id": ticket_id,
                "performer_type": performer_type,
                "performer_id": performer_id,
                "activity": activity
            }

    def get_ticket(self):
        return self.ticket


class Activity:
    """Defines the activity structure. One activity can be added to a
    Ticket. Notes and Tasks can be added to an activity using the
    'add_to_activity function."""

    def __init__(self):
        self.activity = dict()

    def get_activity(self):
        return self.activity

    def add_to_activity(self, new_dict):
        self.activity = {**self.activity, **new_dict}


class Note:
    """Defines note contents, can be added to activities."""

    def __init__(self,
                 note_id,
                 note_type):
        self.note = \
            {
                "note": {
                    "id": note_id,
                    "type": note_type
                }
            }

    def get_note(self):
        return self.note


class Task:
    """Defines the attributes of a task, can be added to an activity."""

    def __init__(self,
                 shipping_address,
                 shipment_date,
                 category,
                 contacted_customer,
                 issue_type,
                 source,
                 status,
                 priority,
                 group,
                 agent_id,
                 requester,
                 product):
        self.task = \
            {
                "shipping_address": shipping_address,
                "shipment_date": shipment_date,
                "category": category,
                "contacted_customer": contacted_customer,
                "issue_type": issue_type,
                "source": source,
                "status": status,
                "priority": priority,
                "group": group,
                "agent_id": agent_id,
                "requester": requester,
                "product": product
            }

    def get_task(self):
        return self.task


class Generator:
    """Object containing functions needed to randomly generate Tickets."""

    # Field options
    activity_types = ["task",
                      "note",
                      "task and note"]

    performer_types = ["user", "admin"]
    shipping_addresses = ["N/A",
                          "1/22 Constance Street, Fortitude Valley, QLD 4006",
                          "6/24-30 Wellington Street, Level 1, Waterloo, NSW 2017",
                          "365 Queen Street, Level 3, Melbourne, VIC 3000",
                          "19 Smith Street, Darwin, NT 0800"]
    categories = ["Phone",
                  "Email",
                  "Enquiry",
                  "Personal"]
    issue_types = ["Incident",
                   "Fault",
                   "Software Installation",
                   "Hardware Replacement",
                   "Instructional",
                   "Other"]
    statuses = ["Open",
                "Closed",
                "Resolved",
                "Waiting for Customer",
                "Waiting for Third Party",
                "Pending"]
    groups = ["refund",
              "repair",
              "troubleshoot",
              "installation"]
    products = ["mobile",
                "laptop",
                "desktop",
                "tablet",
                "peripheral",
                "audiovisual"]

    def __init__(self):
        report_to = datetime.now().replace(tzinfo=timezone.utc)
        report_from = report_to + timedelta(days=-1, seconds=1)

        self.date_range = [report_from, report_to]

    def generate_report(self, number):
        """Coordinates the generation of Activities and Tickets, and compiles
         them into a Report."""
        report = Report()

        count = 1
        note_count = 0
        while count <= number:
            """This is the generation loop. First an Activity of random type
            is made, which is attached to a newly created Ticket. The Ticket
            is then added to the Report."""

            activity_type = self.activity_types[
                r.randrange(0, len(self.activity_types))
            ]
            ticket_performed_at = self.performed_at_scaled(count, number)

            switch = {
                "task": Task(
                    self.random_index(self.shipping_addresses),
                    ticket_performed_at.strftime("%d %b, %Y"),
                    self.random_index(self.categories),
                    bool(r.getrandbits(1)),
                    self.random_index(self.issue_types),
                    r.randrange(1, 9),
                    self.random_index(self.statuses),
                    r.randrange(1, 5),
                    self.random_index(self.groups),
                    r.randrange(145000, 145010),
                    r.randrange(268000, 268050),
                    self.random_index(self.products)
                ).get_task(),
                "note": Note(
                    480652 + note_count,
                    r.randrange(1, 5)
                ).get_note()
            }

            activity = Activity()

            if activity_type == "task":
                activity.add_to_activity(switch.get("task"))
            elif activity_type == "note":
                activity.add_to_activity(switch.get("note"))
                note_count += 1
            elif activity_type == "task and note":
                activity.add_to_activity(switch.get("note"))
                note_count += 1
                activity.add_to_activity(switch.get("task"))

            ticket = Ticket(
                ticket_performed_at.strftime("%d-%m-%Y %X %z"),
                675210 + count,
                self.performer_types[r.getrandbits(1)],
                r.randrange(100, 120),
                activity.get_activity()
            )

            report.add_ticket(ticket.get_ticket())

            count += 1

        return report.create_report(self.date_range)

    @staticmethod
    def random_index(field):
        return field[r.randrange(0, len(field))]

    def performed_at_scaled(self, count, number):
        """Spreads the 'performed_at' field evenly over the date range."""
        increment = (self.date_range[1] - self.date_range[0]) * (
                    count / number)
        return self.date_range[0] + increment


def number_is_valid(number):
    """Argv 'number' validator, ensures minimum (1) entered number of
    tickets """

    valid = False

    if number > 0:
        valid = True
    else:
        raise ValueError

    return valid


def create_file(output, contents):
    """Handles the filename and extension while creating the JSON file."""

    filename = ''

    if output[-5:] == '.json':
        filename = output
    else:
        filename = output + '.json'

    with open(filename, 'w') as file:
        json.dump(contents, file, indent=4)


if __name__ == "__main__":
    run(args.number, args.output)
