import datetime
import string
import logging
from dataclasses import dataclass
import pandas as pd
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
            print(self.bcu_expiry)
            print(type(self.bcu_expiry))
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
        logging.debug(individual)
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
            logging.warning(f"🚨 Category is missing.")
            continue

        entry = db.Entry(entry_number=number, category_id=category.id, race_id=race.id)
        session.add(entry)

        for individual in individuals:
            logging.info(individual)

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

            club = session.query(db.Club).get(individual.club)

            paddler.crews.append(
                db.Crew(
                    club=club,
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
    entry = session.query(db.Entry).get(entry_id)

    if request.method == "POST":
        paddler_id = request.form.get("paddler_id")
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
                race_id = request.form["race_id"]
                entry = db.Entry(race_id=race_id)
                session.add(entry)

            # Update category.
            category_id = request.form["category_id"]
            entry.category_id = category_id

        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry.id))

    races = session.query(db.Race).all()
    paddlers = (
        session.query(db.Paddler).order_by(db.Paddler.first, db.Paddler.last).all()
    )
    categories = session.query(db.Category).all()
    return render_template(
        "entry.j2",
        entry=entry,
        categories=categories,
        races=races,
        paddlers=paddlers,
    )


@blueprint.route("/entry/<entry_id>/number", methods=("GET", "POST"))
@login_required
def number_update(entry_id):
    entry = session.query(db.Entry).get(entry_id)

    if request.method == "POST":
        # Deallocate old number (if still allocated).
        if entry.race_number:
            allocated = (
                session.query(db.NumberAllocation)
                .filter(db.NumberAllocation.entry_id == entry.id)
                .one()
            )
            session.delete(allocated)

        # Allocate new number.
        allocation = db.NumberAllocation(
            number_id=request.form["number"], entry_id=entry.id
        )
        session.add(allocation)
        session.commit()

        return redirect(url_for("kanoe.entry", entry_id=entry.id))

    sub_query = (
        session.query(db.NumberAllocation.number_id, db.NumberAllocation.entry_id)
        .join(db.Entry, db.NumberAllocation.entry_id == db.Entry.id)
        .filter(db.Entry.race_id == entry.race_id)
        .subquery()
    )
    unallocated = (
        session.query(db.Number)
        .outerjoin(sub_query, sub_query.c.number_id == db.Number.id)
        .filter(sub_query.c.entry_id == None)
        .all()
    )

    return render_template("entry-race-number.j2", entry=entry, numbers=unallocated)


@blueprint.route("/entry/<entry_id>/number/deallocate", methods=("GET", "POST"))
@login_required
def number_deallocate(entry_id):
    entry = session.query(db.Entry).get(entry_id)

    allocated = (
        session.query(db.NumberAllocation)
        .filter(db.NumberAllocation.entry_id == entry.id)
        .one()
    )
    session.delete(allocated)
    session.commit()

    return redirect(url_for("kanoe.race", race_id=entry.race_id))


@blueprint.route("/entry/<entry_id>/register", methods=(["GET"]))
@login_required
def entry_register(entry_id):
    entry = session.query(db.Entry).get(entry_id)
    entry.registered = True
    session.commit()

    return redirect(url_for("kanoe.entry", entry_id=entry_id))
