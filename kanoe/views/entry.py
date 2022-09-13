import datetime
import string
from dataclasses import dataclass

import database as db
from database import logger

session = db.Session()

CATEGORY_MAPPING = {
    "SK2": "K2 Senior",
    "JK2": "K2 Junior",
    "WK2": "K2 Ladies",
    "JWK2": "K2 Junior Ladies",
    "VK2": "K2 Veteran",
    "MixK2": "K2 Mixed",
    "JVK2": "K2 Junior/Veteran",
    "SK1": "K1 Senior",
    "JK1": "K1 Junior",
    "WK1": "K1 Ladies",
    "VK1": "K1 Veteran",
    "C2": "C2",
    "C1": "C1",
}


def category_mapping(category):
    try:
        return CATEGORY_MAPPING[category]
    except KeyError:
        logger.warning(f"🚨 Unable to map category '{category}'.")


@dataclass
class Individual:
    number: int
    bcu: int
    bcu_expiry: datetime.date
    first: str
    last: str
    club: str
    klass: str
    category: str
    division: int


def load_entries(race, individuals):
    # Group entries (this handles K1 versus K2).
    entries = {}
    for individual in individuals:
        individual = Individual(**individual)
        individual.first = string.capwords(individual.first)
        individual.last = string.capwords(individual.last)
        individual.category = category_mapping(individual.category)
        logger.info(individual)

        # Check for existing entry.
        #
        if individual.number not in entries:
            logger.info(f"Add new entry: {individual.number}.")
            entries[individual.number] = []

        entries[individual.number].append(individual)

    for number, individuals in entries.items():
        logger.info(f"Entry: {number}.")

        # category = session.query(db.Category).get(individual.category)
        category = [individual.category for individual in individuals]
        # Unique categories.
        category = list(set(category))
        assert len(category) == 1
        category = category[0]
        if category:
            # session.query(db.Club).get(individual.club)
            print(category)
            category = (
                session.query(db.Category).filter(db.Category.label == category).one()
            )
            print(category)
        else:
            logger.warning(f"🚨 Category is missing.")
            continue

        entry = db.Entry(entry_number=number, category_id=category.id, race_id=race.id)
        session.add(entry)

        for individual in individuals:
            logger.info(f"- {individual}.")

            # Look for existing paddler.
            try:
                paddler = (
                    session.query(db.Paddler)
                    .filter(
                        db.Paddler.first == individual.first,
                        db.Paddler.last == individual.last,
                        db.Paddler.division == individual.division,
                    )
                    .one()
                )
            except db.NoResultFound:
                logger.debug("Paddler not found.")
                paddler = db.Paddler(
                    first=individual.first,
                    last=individual.last,
                    division=individual.division,
                )
                session.add(paddler)
            else:
                logger.debug(f"Paddler found: {paddler}.")
                print(paddler)

            club = session.query(db.Club).get(individual.club)

            paddler.seats.append(db.Seat(club=club, entry_id=entry.id))

    session.commit()
