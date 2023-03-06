import datetime
import string
import logging
from dataclasses import dataclass
import pandas as pd
import numpy as np
from flask_login import login_required

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


def load_xlsx(path):
    data = pd.read_excel(path, sheet_name=None)

    def prepare_sheet(df):
        df.columns = [re.sub(" ", "_", col) for col in df.columns.str.lower()]
        # Strip off "BC" prefix (not always present?).
        #
        # BC - British Canoeing
        # SCA - Scottish Canoe Association
        #
        df["bc_number"] = df["bc_number"].str.replace("^(BC|SCA) +", "", regex=True)
        # Remove any remaining text (but only if there are no numbers!).
        df["bc_number"] = df["bc_number"].str.replace("^[^0-9]+", "", regex=True)
        # Empty string is missing.
        df["bc_number"] = df["bc_number"].replace("", np.NaN)
        df["bc_number"] = df["bc_number"].astype("Int64")
        return df

    for key in list(data):
        if key not in CATEGORY_MAPPING.keys():
            data.pop(key)
        else:
            data[key] = prepare_sheet(data[key])
            data[key]["category"] = key

    data = pd.concat(data)

    data = data.rename(
        columns={
            "div": "division",
            "surname": "last",
            "first_name": "first",
            "bc_number": "bcu",
            "expiry": "bcu_expiry",
            "class": "klass",
        }
    )

    return data[
        [
            "number",
            "category",
            "division",
            "last",
            "first",
            "bcu",
            "bcu_expiry",
            "club",
            "klass",
            "due",
            "paid",
        ]
    ]


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
    due: float

    def __post_init__(self):
        if self.bcu_expiry:
            if pd.isnull(self.bcu_expiry):
                self.bcu_expiry = None
            else:
                self.bcu_expiry = str(self.bcu_expiry)
                self.bcu_expiry = datetime.datetime.strptime(
                    self.bcu_expiry, "%Y-%m-%d %H:%M:%S"
                )
        if pd.isnull(self.bcu):
            self.bcu = None
        if self.division:
            try:
                self.division = int(self.division)
            except ValueError:
                self.division = None


def load_entries(race, individuals):
    individuals = individuals.to_dict("records")
    # Group entries (this handles K1 versus K2).
    entries = {}
    for individual in individuals:
        individual = Individual(**individual)
        individual.first = string.capwords(individual.first)
        individual.last = string.capwords(individual.last)
        individual.category = category_mapping(individual.category)

        # Check for existing entry.
        #
        if individual.number not in entries:
            logging.debug(f"Add new entry: {individual.number}.")
            entries[individual.number] = []

        entries[individual.number].append(individual)

    clubs = session.query(db.Club).all()
    #
    clubs = {club.code_regex: club.id for club in clubs}

    for number, individuals in entries.items():
        logging.info(f"Entry: {number}.")

        category = [individual.category for individual in individuals]
        # Unique categories.
        category = list(set(category))
        assert len(category) == 1
        category = category[0]
        if category:
            category = (
                session.query(db.Category).filter(db.Category.label == category).one()
            )
        else:
            logging.warning("🚨 Category is missing.")
            continue

        entry = db.Entry(entry_number=number, category_id=category.id, race_id=race.id)
        session.add(entry)

        for individual in individuals:
            paddler = None

            # Look for existing paddler.
            #
            if not paddler:
                try:
                    logging.debug("Matching paddler using name & BCU number.")
                    paddler = (
                        session.query(db.Paddler)
                        .filter(
                            db.Paddler.first == individual.first,
                            db.Paddler.last == individual.last,
                            db.Paddler.bcu == individual.bcu,
                        )
                        .one()
                    )
                    logging.debug("Paddler found.")
                except db.NoResultFound:
                    logging.debug("Paddler not found.")

            if not paddler:
                try:
                    logging.debug("Matching paddler using name & division.")
                    paddler = (
                        session.query(db.Paddler)
                        .filter(
                            db.Paddler.first == individual.first,
                            db.Paddler.last == individual.last,
                            db.Paddler.division == individual.division,
                        )
                        .one()
                    )
                    logging.debug("Paddler found.")
                except db.NoResultFound:
                    logging.debug("Paddler not found.")

            if not paddler:
                logging.debug("Create new paddler.")
                paddler = db.Paddler(
                    first=individual.first,
                    last=individual.last,
                    division=individual.division,
                )
                session.add(paddler)

            if individual.bcu:
                logging.debug("Update BCU number.")
                paddler.bcu = individual.bcu
            if individual.bcu_expiry:
                logging.debug("Update BCU number expiry.")
                paddler.bcu_expiry = individual.bcu_expiry

            # Search for matching club.
            #
            club_id = []
            #
            logging.debug(f"Searching for club '{individual.club}'.")
            for regex, id in clubs.items():
                if re.match(regex, individual.club):
                    club_id.append(id)
                    logging.debug("Matching club found.")

            if len(club_id) == 0:
                abort(404, description=f"No matched club ('{individual.club}')!")
            elif len(club_id) == 1:
                club_id = club_id[0]
            else:
                abort(404, description=f"Multiple matched clubs ('{individual.club}')!")

            paddler.crews.append(
                db.Crew(
                    club_id=club_id,
                    entry_id=entry.id,
                    due=individual.due,
                    paid=individual.paid,
                )
            )

    session.commit()


@blueprint.route("/entry/<entry_id>", methods=("GET", "POST"))
@blueprint.route("/entry/", defaults={"entry_id": None}, methods=("GET", "POST"))
@login_required
def entry(entry_id):
    entry = session.get(db.Entry, entry_id)
    race_id = request.args.get("race_id")
    #
    races = session.query(db.Race)
    if race_id:
        races = races.filter(db.Race.id == race_id)
    races = races.all()

    if request.method == "POST":
        if request.form.get("action") == "delete":
            logging.info(f"Delete entry (ID = {entry.id}).")
            for crew in entry.crews:
                logging.info("Delete crew (ID = {crew.id}).")
                session.delete(crew)
            session.delete(entry)

            session.commit()

            return redirect(url_for("kanoe.race", race_id=entry.race.id))
        else:
            paddler_id = request.form.get("paddler_id")
            race_id = request.form["race_id"]
            category_id = request.form["category_id"]

            if paddler_id:
                logging.info("Add paddler to entry.")
                crew = db.Crew(
                    paddler_id=paddler_id,
                    entry_id=entry.id,
                )
                session.add(crew)
            else:
                # This is a new entry.
                if entry is None:
                    logging.info("Create new entry.")
                    entry = db.Entry(race_id=race_id)
                    session.add(entry)
                else:
                    # Update race.
                    if entry.race_id != race_id:
                        entry.race_id = race_id

                # Update category.
                entry.category_id = category_id

            # Either assign new number or remove existing number.
            race_number = request.form.get("race_number")
            entry.race_number = session.get(db.Number, race_number)

            session.commit()

            return redirect(url_for("kanoe.entry", entry_id=entry.id))

    categories = session.query(db.Category).all()

    # Only consider race numbers for existing entry.
    if entry:
        # Find numbers which are already allocated for this race.
        taken = (
            session.query(db.NumberAllocation.number_id)
            .join(db.Entry, db.NumberAllocation.entry_id == db.Entry.id)
            .filter(db.Entry.race_id == entry.race_id)
            .subquery()
        )
        # Do LEFT JOIN  between numbers and taken numbers.
        numbers = (
            session.query(db.Number.id)
            .join(taken, db.Number.id == taken.c.number_id, isouter=True)
            .filter(
                (db.Number.lost == False) | (db.Number.lost == None)  # noqa: E711, E712
            )
            .order_by(db.Number.id)
        )
        # Filter out only numbers which are not taken (and possibly the already selected number).
        if entry.race_number:
            numbers = numbers.filter(
                (taken.c.number_id == entry.race_number.id)
                | (taken.c.number_id == None)  # noqa: E711
            )
        else:
            numbers = numbers.filter((taken.c.number_id == None))  # noqa: E711
        # Just get the number IDs.
        numbers = [r.id for r in numbers]
    else:
        numbers = []

    return render_template(
        "entry.j2",
        entry=entry,
        categories=categories,
        races=races,
        numbers=numbers,
    )


@blueprint.route("/entry/<entry_id>/register", methods=(["GET"]))
@login_required
def entry_register(entry_id):
    entry = session.get(db.Entry, entry_id)
    entry.registered = True
    session.commit()

    return redirect(url_for("kanoe.entry", entry_id=entry_id))


@blueprint.route("/entry/<entry_id>/crew/add", methods=(["GET", "POST"]))
@login_required
def entry_crew_add(entry_id):
    entry = session.get(db.Entry, entry_id)

    if request.method == "POST":
        paddler_id = request.form.get("paddler_id")
        if paddler_id:
            logging.info("Add paddler to entry.")
            crew = db.Crew(
                paddler_id=paddler_id,
                entry_id=entry.id,
            )
            session.add(crew)

        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry.id))

    paddlers = (
        session.query(db.Paddler).order_by(db.Paddler.first, db.Paddler.last).all()
    )
    return render_template(
        "entry-crew-add.j2",
        entry=entry,
        paddlers=paddlers,
    )
