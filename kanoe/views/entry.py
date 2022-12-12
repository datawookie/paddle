import datetime
import string
import logging
from dataclasses import dataclass

from .common import *

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
        logging.warning(f"🚨 Unable to map category '{category}'.")


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
    paid: float


def load_entries(race, individuals):
    # Group entries (this handles K1 versus K2).
    entries = {}
    for individual in individuals:
        individual = Individual(**individual)
        individual.first = string.capwords(individual.first)
        individual.last = string.capwords(individual.last)
        individual.category = category_mapping(individual.category)
        logging.info(individual)

        # Check for existing entry.
        #
        if individual.number not in entries:
            logging.info(f"Add new entry: {individual.number}.")
            entries[individual.number] = []

        entries[individual.number].append(individual)

    for number, individuals in entries.items():
        logging.info(f"Entry: {number}.")

        # category = session.query(db.Category).get(individual.category)
        category = [individual.category for individual in individuals]
        # Unique categories.
        category = list(set(category))
        assert len(category) == 1
        category = category[0]
        if category:
            # session.query(db.Club).get(individual.club)
            category = (
                session.query(db.Category).filter(db.Category.label == category).one()
            )
        else:
            logging.warning(f"🚨 Category is missing.")
            continue

        entry = db.Entry(entry_number=number, category_id=category.id, race_id=race.id)
        session.add(entry)

        for individual in individuals:
            logging.info(f"- {individual}.")

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
                logging.debug("Paddler not found.")
                paddler = db.Paddler(
                    first=individual.first,
                    last=individual.last,
                    division=individual.division,
                )
                session.add(paddler)
            else:
                logging.debug(f"Paddler found: {paddler}.")

            club = session.query(db.Club).get(individual.club)

            paddler.seats.append(
                db.Seat(club=club, entry_id=entry.id, paid=individual.paid)
            )

    session.commit()


@blueprint.route("/entry/<entry_id>", methods=("GET", "POST"))
def entry(entry_id):
    entry = session.query(db.Entry).get(entry_id)

    if request.method == "POST":
        entry.category = (
            session.query(db.Category)
            .filter(db.Category.label == request.form["category"])
            .one()
        )
        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry_id))

    return render_template("entry.j2", entry=entry, categories=db.CATEGORY_LIST)
