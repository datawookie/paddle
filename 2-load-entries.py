import sys
import json
import logging
from dataclasses import dataclass

import database as db
from database import logger

session = db.Session()


@dataclass
class Individual:
    number: int
    bcu: int
    first: str
    last: str
    club: str
    category: str
    division: int


def load_entries(individuals):
    # Group entries (this handles K1 versus K2).
    entries = {}
    for individual in individuals:
        individual = Individual(**individual)
        logger.info(individual)

        # Check for existing entry.
        #
        if individual.number not in entries:
            logger.info(f"Add new entry: {individual.number}.")
            entries[individual.number] = []

        entries[individual.number].append(individual)

    for number, individuals in entries.items():
        logger.info(f"Entry: {number}.")
        entry = db.Entry(entry_number=number)
        session.add(entry)
        for individual in individuals:
            logger.info(f"- {individual}.")

            paddler = db.Paddler(
                first=individual.first,
                last=individual.last,
                division=individual.division,
            )
            session.add(paddler)

            club = session.query(db.Club).get(individual.club)

            paddler.seats.append(db.Seat(club=club, entry_id=entry.id))

        session.commit()


if __name__ == "__main__":
    PATH = sys.argv[1]
    with open(PATH, "rt") as file:
        entries = file.read()

    load_entries(json.loads(entries))
